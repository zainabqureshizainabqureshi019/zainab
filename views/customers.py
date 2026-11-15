from views._crud import render_crud

def render():
    render_crud("Customers", "Maintain customer information and purchase history.", "customers", "customer_id",
        [{"col": "name", "label": "Customer name", "required": True}, {"col": "phone", "label": "Phone"}], "Customer",
        extras={"total_bills": "(SELECT COUNT(*) FROM sales s WHERE s.customer_id = t.customer_id)"})
