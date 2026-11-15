import streamlit as st
import db, styles

def render():
    styles.page_header(
        "Products",
        "Manage your product catalogue, pricing, suppliers, and opening stock.",
    )
    tab1, tab2 = st.tabs(["Product catalogue", "Add product"])
    with tab1:
        search = st.text_input(
            "Search products",
            placeholder="Search by product name or SKU",
        )
        df = db.query_df("""SELECT p.product_id, p.name, p.sku, c.name AS category, s.name AS supplier,
            p.cost_price, p.sale_price, COALESCE(i.quantity,0) AS stock, p.reorder_level
            FROM products p LEFT JOIN categories c USING(category_id) LEFT JOIN suppliers s USING(supplier_id)
            LEFT JOIN inventory i USING(product_id) WHERE p.active = TRUE AND (p.name ILIKE %s OR COALESCE(p.sku,'') ILIKE %s)
            ORDER BY p.name""", (f"%{search}%",f"%{search}%"))
        st.dataframe(df, hide_index=True, use_container_width=True)
    with tab2:
        st.subheader("Product details")
        cats = db.query_df("SELECT category_id,name FROM categories ORDER BY name")
        sups = db.query_df("SELECT supplier_id,name FROM suppliers ORDER BY name")
        if cats.empty: st.warning("Add at least one category before creating products.")
        else:
            with st.form("add_product", clear_on_submit=True):
                name = st.text_input("Product name *")
                sku = st.text_input("SKU / barcode")
                category = st.selectbox("Category", cats.category_id.tolist(), format_func=lambda x: cats.loc[cats.category_id==x,'name'].iloc[0])
                supplier = st.selectbox("Supplier (optional)", [None]+sups.supplier_id.tolist(), format_func=lambda x: "Not assigned" if x is None else sups.loc[sups.supplier_id==x,'name'].iloc[0])
                a,b,c = st.columns(3)
                cost = a.number_input("Cost price", min_value=0.0, step=10.0)
                price = b.number_input("Sale price", min_value=0.0, step=10.0)
                opening = c.number_input("Opening stock", min_value=0, step=1)
                reorder = st.number_input("Low-stock alert level", min_value=0, value=5, step=1)
                go = st.form_submit_button("Save product", type="primary")
            if go:
                if not name.strip(): st.error("Product name is required.")
                elif price < cost: st.warning("Sale price is lower than cost price. Please confirm your pricing.")
                else:
                    try:
                        with db.connection() as conn:
                            with conn.cursor() as cur:
                                cur.execute("INSERT INTO products(name,sku,category_id,supplier_id,cost_price,sale_price,reorder_level) VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING product_id",
                                    (name.strip(),sku.strip() or None,category,supplier,cost,price,int(reorder)))
                                pid=cur.fetchone()[0]
                                cur.execute("INSERT INTO inventory(product_id,quantity) VALUES(%s,%s)",(pid,int(opening)))
                        st.success("Product saved successfully."); st.rerun()
                    except Exception as exc: st.error(f"Could not save product. Check SKU uniqueness. ({exc})")
