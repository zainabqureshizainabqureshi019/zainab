from decimal import Decimal

import streamlit as st
import db, styles

def render():
    styles.page_header(
        "Purchases",
        "Record supplier deliveries, track purchase costs, and update stock.",
    )
    products=db.query_df("SELECT product_id,name,cost_price FROM products WHERE active=TRUE ORDER BY name")
    suppliers=db.query_df("SELECT supplier_id,name FROM suppliers ORDER BY name")
    st.subheader("Receive stock")
    with st.form("record_purchase"):
        if products.empty: st.warning("Add a product before recording a delivery.")
        product=st.selectbox("Product",products.product_id.tolist() if not products.empty else [],format_func=lambda x:products.loc[products.product_id==x,'name'].iloc[0] if not products.empty else "")
        supplier=st.selectbox("Supplier",[None]+suppliers.supplier_id.tolist(),format_func=lambda x:"Not assigned" if x is None else suppliers.loc[suppliers.supplier_id==x,'name'].iloc[0])
        qty=st.number_input("Quantity received",min_value=1,value=1,step=1)
        cost=st.number_input("Unit cost",min_value=0.0,step=0.01,format="%.2f")
        note=st.text_input("Reference / notes")
        go=st.form_submit_button("Save purchase",type="primary",disabled=products.empty)
    if go:
        try:
            unit_cost = Decimal(str(cost))
            total_amount = unit_cost * int(qty)
            with db.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("INSERT INTO purchases(supplier_id,notes,total_amount) VALUES(%s,%s,%s) RETURNING purchase_id",(supplier,note,total_amount))
                    pid=cur.fetchone()[0]
                    cur.execute("INSERT INTO purchase_items(purchase_id,product_id,quantity,unit_cost) VALUES(%s,%s,%s,%s)",(pid,int(product),int(qty),unit_cost))
                    cur.execute("INSERT INTO inventory(product_id,quantity) VALUES(%s,%s) ON CONFLICT(product_id) DO UPDATE SET quantity=inventory.quantity+EXCLUDED.quantity,updated_at=NOW()",(int(product),int(qty)))
                    cur.execute("UPDATE products SET cost_price=%s WHERE product_id=%s",(unit_cost,int(product)))
            st.success(f"Purchase #{pid} recorded and stock updated.")
        except Exception as exc: st.error(f"Purchase could not be saved: {exc}")
    st.divider(); st.subheader("Recent purchase history")
    df=db.query_df("SELECT pu.purchase_id,pu.purchase_date,COALESCE(s.name,'—') AS supplier,pu.total_amount,pu.notes FROM purchases pu LEFT JOIN suppliers s USING(supplier_id) ORDER BY pu.purchase_date DESC LIMIT 100")
    st.dataframe(df,hide_index=True,use_container_width=True)
