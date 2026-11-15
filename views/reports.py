
"""Reports and analytics page for Smart Inventory."""

import streamlit as st
import plotly.graph_objects as go

import db
import styles


CHART_COLORS = ["#245B91", "#20A39E", "#8064A2", "#F4A261"]


def render():
    styles.page_header(
        "Reports & Analytics",
        "Explore recent sales performance and your current stock position.",
    )

    sales = db.query_df("""
        SELECT
            sale_date::date AS day,
            SUM(total_amount) AS revenue,
            COUNT(*) AS bills
        FROM sales
        WHERE sale_date >= CURRENT_DATE - INTERVAL '29 days'
          AND sale_date < CURRENT_DATE + INTERVAL '1 day'
        GROUP BY sale_date::date
        ORDER BY day
    """)

    products = db.query_df("""
        SELECT
            p.name,
            COALESCE(i.quantity,0) AS stock,
            p.reorder_level
        FROM products p
        LEFT JOIN inventory i USING(product_id)
        WHERE p.active=TRUE
        ORDER BY stock ASC
    """)

    total_revenue = (
        float(sales["revenue"].sum()) if not sales.empty else 0
    )

    total_bills = (
        int(sales["bills"].sum()) if not sales.empty else 0
    )

    a, b = st.columns(2)

    a.metric(
        "Revenue (last 30 days)",
        f"Rs. {total_revenue:,.2f}"
    )

    b.metric(
        "Bills (last 30 days)",
        total_bills
    )

    st.divider()
    st.subheader("Daily sales · Last 30 days")

    if sales.empty:
        st.info("Sales reports will appear after your first sale.")
    else:
        colors = [
            CHART_COLORS[i % len(CHART_COLORS)]
            for i in range(len(sales))
        ]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=sales["day"],
            y=sales["revenue"],
            marker=dict(
                color=colors,
                line=dict(color="rgba(255,255,255,0.8)", width=1)
            ),
            text=[
                f"Rs. {float(value):,.0f}"
                for value in sales["revenue"]
            ],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b><br>"
                "Revenue: Rs. %{y:,.2f}"
                "<extra></extra>"
            ),
        ))

        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=30, b=10),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            bargap=0.30,
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
                title="Revenue (Rs.)",
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

    st.divider()
    st.subheader("Current stock position")

    if products.empty:
        st.info("No products to report yet.")
    else:
        st.dataframe(
            products,
            hide_index=True,
            use_container_width=True
        )

    if not sales.empty or not products.empty:
        st.divider()
        st.subheader("Export reports")

        sales_column, stock_column = st.columns(2)

        if not sales.empty:
            sales_column.download_button(
                "Download sales report",
                sales.to_csv(index=False).encode("utf-8"),
                "sales_report.csv",
                "text/csv",
                use_container_width=True,
            )

        if not products.empty:
            stock_column.download_button(
                "Download stock report",
                products.to_csv(index=False).encode("utf-8"),
                "stock_report.csv",
                "text/csv",
                use_container_width=True,
            )
