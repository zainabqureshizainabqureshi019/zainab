from decimal import Decimal
from html import escape

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import db
import styles


def _format_amount(value) -> str:
    return f"{Decimal(str(value)):,.2f}"


def _receipt_html(sale, items: pd.DataFrame) -> str:
    item_rows = "".join(
        f"""
        <tr>
          <td>{escape(str(item.name))}</td>
          <td class="numeric">{int(item.quantity)}</td>
          <td class="numeric">{_format_amount(item.unit_price)}</td>
          <td class="numeric">{_format_amount(item.line_total)}</td>
        </tr>
        """
        for item in items.itertuples(index=False)
    )
    sold_at = sale["sale_date"]
    if hasattr(sold_at, "strftime"):
        sold_at = sold_at.strftime("%b %d, %Y at %I:%M %p")

    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          * {{ box-sizing: border-box; }}
          body {{
            margin: 0;
            padding: 1.25rem;
            background: #f3f6fa;
            color: #16263f;
            font-family: Arial, Helvetica, sans-serif;
          }}
          .receipt {{
            max-width: 760px;
            margin: 0 auto;
            overflow: hidden;
            border: 1px solid #e3e9f0;
            border-radius: 12px;
            background: #ffffff;
            box-shadow: 0 4px 18px #172b4d12;
          }}
          .receipt-header {{
            padding: 26px 30px 21px;
            border-bottom: 1px solid #e9edf2;
          }}
          .brand {{
            color: #245b91;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2px;
          }}
          h1 {{
            margin: 12px 0 4px;
            font-size: 25px;
            letter-spacing: -0.5px;
          }}
          .muted {{ color: #68778c; }}
          .bill-meta {{
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-top: 20px;
            font-size: 13px;
            line-height: 1.8;
          }}
          .bill-meta strong {{ color: #16263f; }}
          .receipt-body {{ padding: 20px 30px 26px; }}
          table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
          }}
          th {{
            padding: 11px 8px;
            background: #f4f7fa;
            color: #53647b;
            font-size: 10px;
            letter-spacing: 0.7px;
            text-align: left;
            text-transform: uppercase;
          }}
          td {{
            padding: 12px 8px;
            border-bottom: 1px solid #edf0f4;
            vertical-align: top;
          }}
          .numeric {{ text-align: right; white-space: nowrap; }}
          .total-row td {{
            padding-top: 17px;
            border-bottom: 0;
            color: #16263f;
            font-size: 16px;
            font-weight: 700;
          }}
          .receipt-footer {{
            padding: 15px 30px 24px;
            color: #68778c;
            font-size: 12px;
            text-align: center;
          }}
          .print-action {{
            display: flex;
            justify-content: flex-end;
            max-width: 760px;
            margin: 0 auto 12px;
          }}
          .print-action button {{
            padding: 10px 18px;
            border: 0;
            border-radius: 7px;
            background: #245b91;
            color: #ffffff;
            cursor: pointer;
            font-size: 13px;
            font-weight: 700;
          }}
          .print-action button:hover {{ background: #1b4a78; }}
          @page {{ size: A4 portrait; margin: 14mm; }}
          @media print {{
            body {{ padding: 0; background: #ffffff; }}
            .receipt {{
              max-width: none;
              overflow: visible;
              border: 0;
              border-radius: 0;
              box-shadow: none;
            }}
            .print-action {{ display: none; }}
            thead {{ display: table-header-group; }}
            tr {{ break-inside: avoid; page-break-inside: avoid; }}
          }}
          @media (max-width: 520px) {{
            body {{ padding: 0.5rem; }}
            .receipt-header {{ padding: 20px 17px 16px; }}
            .receipt-body {{ padding: 16px 12px 20px; }}
            .receipt-footer {{ padding: 14px 16px 20px; }}
            table {{ font-size: 11px; }}
            th {{ padding: 9px 5px; font-size: 9px; }}
            td {{ padding: 10px 5px; }}
          }}
        </style>
      </head>
      <body>
        <div class="print-action">
          <button type="button" onclick="window.print()">Print bill</button>
        </div>
        <main class="receipt">
          <header class="receipt-header">
            <div class="brand">SMART INVENTORY</div>
            <h1>Sales receipt</h1>
            <div class="muted">Thank you for your purchase.</div>
            <div class="bill-meta">
              <div>
                <div><strong>Bill number:</strong> #{int(sale["sale_id"])}</div>
                <div><strong>Date:</strong> {escape(str(sold_at))}</div>
                <div><strong>Customer:</strong> {escape(str(sale["customer"]))}</div>
              </div>
              <div>
                <div><strong>Payment:</strong> {escape(str(sale["payment_method"]))}</div>
                <div><strong>Served by:</strong> {escape(str(sale["cashier"]))}</div>
              </div>
            </div>
          </header>
          <section class="receipt-body">
            <table>
              <thead>
                <tr>
                  <th>Item</th>
                  <th class="numeric">Qty</th>
                  <th class="numeric">Unit price</th>
                  <th class="numeric">Amount</th>
                </tr>
              </thead>
              <tbody>
                {item_rows}
                <tr class="total-row">
                  <td colspan="3">Total</td>
                  <td class="numeric">{_format_amount(sale["total_amount"])}</td>
                </tr>
              </tbody>
            </table>
          </section>
          <footer class="receipt-footer">
            Please retain this bill for your records.
          </footer>
        </main>
      </body>
    </html>
    """


def render():
    styles.page_header("Sales", "Build a multi-product cart and automatically update inventory.")
    products = db.query_df(
        """SELECT p.product_id, p.name, p.sku, p.sale_price,
                  COALESCE(i.quantity, 0) AS stock
           FROM products p
           LEFT JOIN inventory i USING (product_id)
           WHERE p.active = TRUE
           ORDER BY p.name, p.product_id"""
    )
    customers = db.query_df("SELECT customer_id, name FROM customers ORDER BY name")

    if products.empty:
        st.info("Add products before recording a sale.")
    else:
        product_labels = {}
        for product in products.itertuples(index=False):
            sku = (
                f" ({product.sku})"
                if pd.notna(product.sku) and str(product.sku).strip()
                else f" (ID {product.product_id})"
            )
            label = f"{product.name}{sku}"
            product_labels[label] = int(product.product_id)

        st.subheader("Product availability")
        st.caption("Review current prices and stock before adding products to the cart.")
        st.dataframe(
            products[["name", "sku", "sale_price", "stock"]],
            hide_index=True,
            use_container_width=True,
        )

        st.subheader("Build your cart")
        st.caption("Choose a product for each row. Use the table controls to add more items.")
        cart_key = f"sale_cart_{st.session_state.get('sale_cart_version', 0)}"
        cart = st.data_editor(
            pd.DataFrame([{"Product": "", "Quantity": 1}]),
            column_config={
                "Product": st.column_config.SelectboxColumn(
                    "Product", options=list(product_labels), required=False
                ),
                "Quantity": st.column_config.NumberColumn(
                    "Quantity", min_value=1, step=1, format="%d"
                ),
            },
            num_rows="dynamic",
            hide_index=True,
            use_container_width=True,
            key=cart_key,
        )
        customer_column, payment_column = st.columns(2)
        with customer_column:
            customer = st.selectbox(
                "Customer (optional)",
                [None] + customers.customer_id.tolist(),
                format_func=lambda value: (
                    "Walk-in customer"
                    if value is None
                    else customers.loc[
                        customers.customer_id == value, "name"
                    ].iloc[0]
                ),
            )
        with payment_column:
            payment = st.selectbox(
                "Payment method", ["Cash", "Card", "Bank transfer", "Other"]
            )

        if st.button("Complete sale", type="primary"):
            try:
                quantities = {}
                for row_number, row in cart.iterrows():
                    label = row.get("Product")
                    if pd.isna(label) or not str(label).strip():
                        continue

                    quantity_value = row.get("Quantity")
                    if (
                        pd.isna(quantity_value)
                        or not float(quantity_value).is_integer()
                        or int(quantity_value) < 1
                    ):
                        raise ValueError(
                            f"Enter a whole quantity of at least 1 on cart row "
                            f"{row_number + 1}."
                        )

                    product_id = product_labels.get(str(label))
                    if product_id is None:
                        raise ValueError(
                            f"Choose a valid product on cart row {row_number + 1}."
                        )
                    quantities[product_id] = (
                        quantities.get(product_id, 0) + int(quantity_value)
                    )

                if not quantities:
                    raise ValueError("Add at least one product to the cart.")

                ordered_ids = sorted(quantities)
                with db.connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            """SELECT product_id, name, sale_price
                               FROM products
                               WHERE product_id = ANY(%s) AND active = TRUE
                               ORDER BY product_id""",
                            (ordered_ids,),
                        )
                        locked_products = {
                            row[0]: {"name": row[1], "sale_price": row[2]}
                            for row in cur.fetchall()
                        }
                        if len(locked_products) != len(ordered_ids):
                            raise ValueError(
                                "A selected product is no longer active. Refresh "
                                "the page and try again."
                            )

                        cur.execute(
                            """SELECT product_id, quantity
                               FROM inventory
                               WHERE product_id = ANY(%s)
                               ORDER BY product_id
                               FOR UPDATE""",
                            (ordered_ids,),
                        )
                        stock_by_product = dict(cur.fetchall())
                        for product_id, quantity in quantities.items():
                            available = stock_by_product.get(product_id, 0)
                            if quantity > available:
                                name = locked_products[product_id]["name"]
                                raise ValueError(
                                    f"Insufficient stock for {name}. "
                                    f"Available quantity: {available}."
                                )

                        total = sum(
                            (
                                locked_products[product_id]["sale_price"] * quantity
                                for product_id, quantity in quantities.items()
                            ),
                            start=0,
                        )
                        cur.execute(
                            """INSERT INTO sales
                                 (customer_id, user_id, payment_method, total_amount)
                               VALUES (%s, %s, %s, %s)
                               RETURNING sale_id""",
                            (
                                customer,
                                st.session_state.user["user_id"],
                                payment,
                                total,
                            ),
                        )
                        sale_id = cur.fetchone()[0]

                        for product_id, quantity in quantities.items():
                            price = locked_products[product_id]["sale_price"]
                            cur.execute(
                                """INSERT INTO sale_items
                                     (sale_id, product_id, quantity, unit_price)
                                   VALUES (%s, %s, %s, %s)""",
                                (sale_id, product_id, quantity, price),
                            )
                            cur.execute(
                                """UPDATE inventory
                                   SET quantity = quantity - %s, updated_at = NOW()
                                   WHERE product_id = %s AND quantity >= %s""",
                                (quantity, product_id, quantity),
                            )
                            if cur.rowcount != 1:
                                raise ValueError(
                                    f"Stock changed while recording "
                                    f"{locked_products[product_id]['name']}. "
                                    "Please try again."
                                )

                st.success(f"Sale #{sale_id} recorded. Total: {total:,.2f}")
                st.session_state["selected_bill_id"] = sale_id
                st.session_state.sale_cart_version = (
                    st.session_state.get("sale_cart_version", 0) + 1
                )
            except Exception as exc:
                st.error(f"Sale was not completed: {exc}")

    st.divider()
    st.subheader("Billing & receipts")
    st.caption("Preview and print a bill for any of the 100 most recent sales.")
    recent_sales = db.query_df(
        """SELECT s.sale_id, s.sale_date, COALESCE(c.name, 'Walk-in') AS customer,
                  s.payment_method, s.total_amount
           FROM sales s
           LEFT JOIN customers c USING (customer_id)
           ORDER BY s.sale_date DESC
           LIMIT 100"""
    )
    st.dataframe(recent_sales, hide_index=True, use_container_width=True)
    if not recent_sales.empty:
           sale_ids = recent_sales["sale_id"].astype(int).tolist()
           if st.session_state.get("selected_bill_id") not in sale_ids:
               st.session_state["selected_bill_id"] = sale_ids[0]
           selected_sale_id = st.selectbox(
               "Select a sale to preview",
               sale_ids,
               format_func=lambda sale_id: (
                   f"Bill #{sale_id} · "
                   f"{recent_sales.loc[recent_sales.sale_id == sale_id, 'customer'].iloc[0]} · "
                   f"{float(recent_sales.loc[recent_sales.sale_id == sale_id, 'total_amount'].iloc[0]):,.2f}"
               ),
               key="selected_bill_id",
           )
           sale = db.query_one(
               """SELECT s.sale_id, s.sale_date,
                         COALESCE(c.name, 'Walk-in customer') AS customer,
                         s.payment_method, s.total_amount,
                         COALESCE(u.username, 'Staff') AS cashier
                  FROM sales s
                  LEFT JOIN customers c USING (customer_id)
                  LEFT JOIN users u USING (user_id)
                  WHERE s.sale_id = %s""",
               (int(selected_sale_id),),
           )
           if sale is None:
               st.error("This sale could not be found. Refresh the page and try again.")
           else:
               items = db.query_df(
                   """SELECT p.name, si.quantity, si.unit_price, si.line_total
                      FROM sale_items si
                      JOIN products p USING (product_id)
                      WHERE si.sale_id = %s
                      ORDER BY si.sale_item_id""",
                   (int(selected_sale_id),),
               )
               if items.empty:
                   st.warning(
                       "This sale has no saved item details, so a printable bill "
                       "cannot be generated."
                   )
               else:
                   st.caption(
                       "Choose Print bill on the preview. In the print dialog, "
                       "select a printer or save the bill as a PDF."
                   )
                   st.subheader(f"Bill preview · #{int(selected_sale_id)}")
                   components.html(
                       _receipt_html(sale, items),
                       height=620,
                       scrolling=True,
                   )
