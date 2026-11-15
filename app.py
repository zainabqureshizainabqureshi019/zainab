
"""Main Streamlit entry point for Smart Inventory & Sales Management System."""

import logging

import streamlit as st
import plotly.graph_objects as go

import db
import styles

from views import (
    categories,
    customers,
    suppliers,
    users,
    products,
    inventory,
    sales,
    purchases,
    reports,
)

logger = logging.getLogger(__name__)

CHART_COLORS = ["#245B91", "#20A39E", "#8064A2", "#F4A261"]


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Inventory",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state=(
        "expanded" if "user" in st.session_state else "collapsed"
    ),
)

styles.apply_styles(authenticated="user" in st.session_state)


# --------------------------------------------------
# ROLE-BASED PAGE PERMISSIONS
# --------------------------------------------------

PAGE_PERMISSIONS = {
    "admin": [
        "Dashboard",
        "Products",
        "Inventory",
        "Sales",
        "Purchases",
        "Categories",
        "Customers",
        "Suppliers",
        "Reports & Analytics",
        "Account & Users",
    ],

    "manager": [
        "Dashboard",
        "Products",
        "Inventory",
        "Sales",
        "Purchases",
        "Categories",
        "Customers",
        "Suppliers",
        "Reports & Analytics",
        "Account & Users",
    ],

    "cashier": [
        "Sales",
        "Account & Users",
    ],
}


# --------------------------------------------------
# LOGIN SCREEN
# --------------------------------------------------

def login_screen():

    st.markdown(
        '<div class="login-page-marker"></div>',
        unsafe_allow_html=True
    )

    intro, sign_in = st.columns([1.08, 0.92], gap="large")

    with intro:

        st.markdown(
            """
            <section class="login-hero">
              <div class="login-brand">
                <span class="login-brand-mark">S</span>
                <span>SMART INVENTORY</span>
              </div>

              <div class="login-copy">
                <h1>Run your store with confidence.</h1>
                <p>
                  A clear view of your products, stock, purchasing, and sales
                  in one simple workspace.
                </p>
              </div>

              <div class="login-feature-list">
                <span class="login-feature">Inventory control</span>
                <span class="login-feature">Sales tracking</span>
                <span class="login-feature">Business reports</span>
              </div>
            </section>
            """,
            unsafe_allow_html=True,
        )

    with sign_in:

        with st.container(border=True):

            st.markdown(
                """
                <div class="login-card-title">Welcome back</div>
                <p class="login-card-subtitle">
                    Sign in with your account to continue to your workspace.
                </p>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form", border=False):

                username = st.text_input(
                    "Username",
                    placeholder="Enter your username"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                submit = st.form_submit_button(
                    "Sign in",
                    type="primary",
                    use_container_width=True
                )

            if submit:

                try:

                    user = db.authenticate(
                        username.strip(),
                        password
                    )

                    if user:

                        if user.get("role", "").lower() not in PAGE_PERMISSIONS:
                            st.error(
                                "Your account has an invalid role. "
                                "Contact your administrator."
                            )
                            return

                        st.session_state.user = user
                        st.rerun()

                    else:
                        st.error("Incorrect username or password.")

                except Exception:

                    logger.exception("Sign-in failed")

                    st.error(
                        "Unable to connect to the database. "
                        "Check DATABASE_URL and run schema.sql in Neon."
                    )

        st.markdown(
            '<div class="login-footnote">Need access? Contact your workspace administrator.</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

def dashboard():

    styles.page_header(
        "Business overview",
        "A real-time snapshot of your products, inventory, and daily sales.",
    )

    stats = db.query_one("""
        SELECT
          (SELECT COUNT(*) FROM products WHERE active=TRUE) AS products,

          (SELECT COALESCE(SUM(quantity),0) FROM inventory) AS units,

          (SELECT COUNT(*) FROM products p
           LEFT JOIN inventory i USING(product_id)
           WHERE p.active=TRUE
           AND COALESCE(i.quantity,0)<=p.reorder_level) AS low_stock,

          (SELECT COALESCE(SUM(total_amount),0) FROM sales
           WHERE sale_date::date=CURRENT_DATE) AS today_sales,

          (SELECT COUNT(*) FROM sales
           WHERE sale_date::date=CURRENT_DATE) AS today_bills
    """)

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Active products", stats["products"])

    c2.metric("Units in stock", stats["units"])

    c3.metric("Low-stock items", stats["low_stock"])

    c4.metric(
        "Today's sales",
        f"{float(stats['today_sales']):,.2f}"
    )

    c5.metric("Today's bills", stats["today_bills"])

    left, right = st.columns([1.4, 1])

    # SALES PERFORMANCE CHART

    with left:

        st.subheader("Sales performance")

        trend = db.query_df("""
            SELECT
                sale_date::date AS day,
                SUM(total_amount) AS revenue
            FROM sales
            WHERE sale_date >= CURRENT_DATE - INTERVAL '13 days'
            GROUP BY sale_date::date
            ORDER BY day
        """)

        if trend.empty:

            st.info(
                "Your sales chart will appear after recording sales."
            )

        else:

            colors = [
                CHART_COLORS[i % len(CHART_COLORS)]
                for i in range(len(trend))
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=trend["day"],
                    y=trend["revenue"],

                    marker=dict(
                        color=colors,
                        line=dict(
                            color="rgba(255,255,255,0.8)",
                            width=1
                        )
                    ),

                    text=[
                        f"Rs. {float(value):,.0f}"
                        for value in trend["revenue"]
                    ],

                    textposition="outside",
                    cliponaxis=False,

                    hovertemplate=(
                        "<b>%{x|%d %b %Y}</b><br>"
                        "Sales: Rs. %{y:,.2f}"
                        "<extra></extra>"
                    ),
                )
            )

            fig.update_layout(
                height=360,

                margin=dict(
                    l=10,
                    r=10,
                    t=25,
                    b=10
                ),

                plot_bgcolor="white",
                paper_bgcolor="white",
                showlegend=False,
                bargap=0.35,

                font=dict(
                    family="Arial",
                    color="#16263F",
                    size=12
                ),

                xaxis=dict(
                    title=None,
                    showgrid=False,
                    tickformat="%d %b",
                    linecolor="#E5EAF0"
                ),

                yaxis=dict(
                    title="Sales Revenue (Rs.)",
                    tickformat=",.0f",
                    rangemode="tozero",
                    gridcolor="#EDF1F5",
                    zeroline=False
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

    # LOW STOCK ALERTS

    with right:

        st.subheader("Low-stock alerts")

        low = db.query_df("""
            SELECT
                p.name,
                COALESCE(i.quantity,0) AS stock,
                p.reorder_level
            FROM products p
            LEFT JOIN inventory i USING(product_id)
            WHERE p.active=TRUE
              AND COALESCE(i.quantity,0)<=p.reorder_level
            ORDER BY stock,p.name
            LIMIT 10
        """)

        if low.empty:

            st.success(
                "No low-stock alerts. Stock levels look good."
            )

        else:

            st.dataframe(
                low,
                hide_index=True,
                use_container_width=True
            )

    # RECENT SALES

    st.subheader("Recent sales")

    recent = db.query_df("""
        SELECT
            s.sale_id,
            s.sale_date,
            COALESCE(c.name,'Walk-in') AS customer,
            s.payment_method,
            s.total_amount
        FROM sales s
        LEFT JOIN customers c USING(customer_id)
        ORDER BY sale_date DESC
        LIMIT 8
    """)

    st.dataframe(
        recent,
        hide_index=True,
        use_container_width=True
    )


# --------------------------------------------------
# CHECK LOGIN
# --------------------------------------------------

if "user" not in st.session_state:

    login_screen()
    st.stop()


# --------------------------------------------------
# CHECK USER ROLE
# --------------------------------------------------

user = st.session_state.user

role = user.get("role", "").lower()

if role not in PAGE_PERMISSIONS:

    st.error(
        "Invalid account role. Please contact your administrator."
    )

    st.session_state.pop("user", None)
    st.rerun()

allowed_pages = PAGE_PERMISSIONS[role]


# --------------------------------------------------
# DATABASE HEALTH CHECK
# --------------------------------------------------

try:

    db.health_check()

except Exception:

    logger.exception("Database health check failed")

    st.error(
        "Database connection lost. Check your Neon connection string "
        "and network connection."
    )

    if st.button("Sign out"):

        st.session_state.pop("user", None)
        st.rerun()

    st.stop()


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">
          <div class="sidebar-brand-mark">S</div>
          <div>
            <div class="sidebar-brand-name">Smart Inventory</div>
            <div class="sidebar-brand-caption">STORE MANAGEMENT</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.caption("SIGNED IN AS")

    st.write(f"**{user['username']}**")

    st.caption(f"{role.upper()} ACCOUNT")

    page = st.radio(
        "WORKSPACE",
        allowed_pages,
        label_visibility="collapsed",
    )

    st.divider()

    if st.button(
        "Sign out",
        use_container_width=True
    ):

        st.session_state.pop("user", None)
        st.rerun()


# --------------------------------------------------
# PAGE ACCESS PROTECTION
# --------------------------------------------------

try:

    if page not in allowed_pages:

        st.error(
            "You do not have permission to access this page."
        )

        st.stop()

    # DASHBOARD

    if page == "Dashboard":

        dashboard()

    # PRODUCTS

    elif page == "Products":

        products.render()

    # INVENTORY

    elif page == "Inventory":

        inventory.render()

    # SALES

    elif page == "Sales":

        sales.render()

    # PURCHASES

    elif page == "Purchases":

        purchases.render()

    # CATEGORIES

    elif page == "Categories":

        categories.render()

    # CUSTOMERS

    elif page == "Customers":

        customers.render()

    # SUPPLIERS

    elif page == "Suppliers":

        suppliers.render()

    # REPORTS

    elif page == "Reports & Analytics":

        reports.render()

    # ACCOUNT AND USERS

    elif page == "Account & Users":

        users.render()


except Exception:

    logger.exception(
        "Page rendering failed: %s",
        page
    )

    st.error(
        "This page could not be loaded. "
        "Check that the database schema is up to date."
    )
