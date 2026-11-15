import streamlit as st
import db, styles

def render():
    styles.page_header(
        "Inventory",
        "Monitor stock on hand and identify products that need replenishment.",
    )
    low = db.query_df("""SELECT p.product_id,p.name,p.sku,COALESCE(i.quantity,0) AS quantity,p.reorder_level
      FROM products p LEFT JOIN inventory i USING(product_id) WHERE p.active=TRUE ORDER BY p.name""")
    if low.empty:
        st.info("Your inventory will appear here after you add your first product.")
        return
    low["status"] = low.apply(lambda r: "Low stock" if r.quantity <= r.reorder_level else "In stock", axis=1)
    a,b = st.columns(2)
    a.metric("Units in stock", int(low.quantity.sum()))
    b.metric("Products below reorder level", int((low.quantity <= low.reorder_level).sum()))
    st.subheader("Stock by product")
    st.dataframe(low, hide_index=True, use_container_width=True)
    st.caption("Purchases increase stock; completed sales reduce it automatically.")
