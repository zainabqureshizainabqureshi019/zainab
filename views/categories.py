from views._crud import render_crud

def render():
    render_crud("Categories", "Organize products into clear product groups.", "categories", "category_id",
        [{"col": "name", "label": "Category name", "required": True}], "Category",
        extras={"products": "(SELECT COUNT(*) FROM products p WHERE p.category_id = t.category_id)"})
