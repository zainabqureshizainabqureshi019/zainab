from views._crud import render_crud

def render():
    render_crud("Suppliers", "Manage the suppliers that provide your stock.", "suppliers", "supplier_id",
        [{"col": "name", "label": "Supplier name", "required": True}, {"col": "phone", "label": "Phone"},
         {"col": "address", "label": "Address"}], "Supplier",
        extras={"products": "(SELECT COUNT(*) FROM products p WHERE p.supplier_id = t.supplier_id)",
                "purchases": "(SELECT COUNT(*) FROM purchases pu WHERE pu.supplier_id = t.supplier_id)"})
