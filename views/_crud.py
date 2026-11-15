"""Reusable CRUD screen for categories, customers and suppliers."""
import pandas as pd
import streamlit as st
import db
import styles


def render_crud(title, subtitle, table, id_col, fields, singular, extras=None, name_col="name"):
    extras = extras or {}
    styles.page_header(title, subtitle)
    is_admin = st.session_state.get("user", {}).get("role") == "admin"
    cols = [f["col"] for f in fields]
    tab_list, tab_add, tab_edit = st.tabs(
        ["All records", f"Add {singular}", "Edit or delete"]
    )
    with tab_list:
        search = st.text_input(
            "Search records",
            placeholder=f"Search {title.lower()}...",
            key=f"search_{table}",
        )
        select_cols = ", ".join(f"t.{column}" for column in cols)
        extra_sql = "".join(f", {expr} AS {alias}" for alias, expr in extras.items())
        where = " OR ".join(f"COALESCE(t.{c}::text, '') ILIKE %s" for c in cols)
        df = db.query_df(
            f"SELECT t.{id_col} AS id, {select_cols}{extra_sql} FROM {table} t "
            f"WHERE {where} ORDER BY t.{name_col}", tuple([f"%{search}%"] * len(cols)))
        if df.empty:
            st.info(f"No {title.lower()} found. Add your first record using the Add tab.")
        else:
            st.caption(f"{len(df)} record(s)")
            st.dataframe(df, hide_index=True, use_container_width=True)
    with tab_add:
        with st.form(f"add_{table}", clear_on_submit=True):
            values = {f["col"]: st.text_input(f["label"] + (" *" if f.get("required") else "")) for f in fields}
            submitted = st.form_submit_button(f"Add {singular}", type="primary", use_container_width=True)
        if submitted:
            missing = [f["label"] for f in fields if f.get("required") and not values[f["col"]].strip()]
            if missing:
                st.error("Required: " + ", ".join(missing))
            else:
                try:
                    db.execute(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})",
                               tuple(values[c].strip() or None for c in cols))
                    st.success(f"{singular} added successfully.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not save this record. Check duplicate values and database constraints. ({exc})")
    with tab_edit:
        records = db.query_df(f"SELECT {id_col} AS id, {', '.join(cols)} FROM {table} ORDER BY {name_col}")
        if records.empty:
            st.info("Nothing to edit yet.")
        else:
            lookup = records.set_index("id")
            rid = st.selectbox("Select a record", lookup.index.tolist(),
                               format_func=lambda i: str(lookup.loc[i, name_col]), key=f"pick_{table}")
            row = lookup.loc[rid]
            with st.form(f"edit_{table}"):
                new = {}
                for f in fields:
                    current = row[f["col"]]
                    new[f["col"]] = st.text_input(f["label"] + (" *" if f.get("required") else ""),
                        value="" if pd.isna(current) else str(current), key=f"edit_{table}_{f['col']}_{rid}")
                save = st.form_submit_button("Save changes", type="primary")
            if save:
                missing = [f["label"] for f in fields if f.get("required") and not new[f["col"]].strip()]
                if missing:
                    st.error("Required: " + ", ".join(missing))
                else:
                    try:
                        db.execute(f"UPDATE {table} SET {', '.join(c + ' = %s' for c in cols)} WHERE {id_col} = %s",
                                   tuple(new[c].strip() or None for c in cols) + (int(rid),))
                        st.success("Changes saved.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not update this record. ({exc})")
            if is_admin:
                st.divider()
                confirm = st.checkbox(f"I understand this permanently deletes {row[name_col]!s}", key=f"confirm_{table}")
                if st.button("Delete record", disabled=not confirm, key=f"delete_{table}"):
                    try:
                        db.execute(f"DELETE FROM {table} WHERE {id_col} = %s", (int(rid),))
                        st.success("Record deleted.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Cannot delete this record because it is used by another record. ({exc})")
