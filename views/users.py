
"""Account and User Management for Smart Inventory."""

import streamlit as st
import db
import styles


ROLES = ["admin", "manager", "cashier"]


def render():
    user = st.session_state.get("user")

    if not user:
        st.error("Please log in first.")
        return

    is_admin = user.get("role") == "admin"

    styles.page_header(
        "Account & Users",
        "Manage your account security and workspace access.",
    )

    tab_names = ["My Account"]
    if is_admin:
        tab_names.append("User Management")

    tabs = st.tabs(tab_names)

    # ---------------------------------
    # MY ACCOUNT
    # ---------------------------------
    with tabs[0]:
        st.subheader("Change Password")
        st.caption("Use a password with at least 8 characters.")

        with st.form("change_password_form", clear_on_submit=True):
            old_password = st.text_input(
                "Current Password", type="password"
            )
            new_password = st.text_input(
                "New Password", type="password"
            )
            confirm_password = st.text_input(
                "Confirm New Password", type="password"
            )

            password_submit = st.form_submit_button(
                "Update Password", type="primary"
            )

        if password_submit:
            if len(new_password) < 8:
                st.error("Password must contain at least 8 characters.")

            elif new_password != confirm_password:
                st.error("New passwords do not match.")

            elif not db.authenticate(
                user["username"], old_password
            ):
                st.error("Current password is incorrect.")

            else:
                db.execute(
                    """
                    UPDATE users
                    SET password_hash = crypt(%s, gen_salt('bf'))
                    WHERE user_id = %s
                    """,
                    (new_password, user["user_id"]),
                )
                st.success("Password updated successfully.")

    # ---------------------------------
    # ADMIN USER MANAGEMENT
    # ---------------------------------
    if is_admin:
        with tabs[1]:
            st.subheader("Workspace Users")
            st.caption(
                "Create accounts, assign roles and manage user access."
            )

            users = db.query_df(
                """
                SELECT user_id, username, role, created_at
                FROM users
                ORDER BY user_id
                """
            )

            st.dataframe(
                users,
                hide_index=True,
                use_container_width=True,
            )

            st.divider()

            # CREATE USER
            st.subheader("Create New User")

            with st.form("create_user_form", clear_on_submit=True):
                new_username = st.text_input("Username")
                new_user_password = st.text_input(
                    "Temporary Password", type="password"
                )

                new_user_role = st.selectbox(
                    "Assign Role",
                    ROLES,
                    format_func=lambda role: role.title(),
                )

                create_submit = st.form_submit_button(
                    "Create User", type="primary"
                )

            if create_submit:
                username = new_username.strip()

                if not username:
                    st.error("Username is required.")

                elif len(new_user_password) < 8:
                    st.error(
                        "Password must contain at least 8 characters."
                    )

                else:
                    try:
                        db.execute(
                            """
                            INSERT INTO users
                                (username, password_hash, role)
                            VALUES
                                (%s, crypt(%s, gen_salt('bf')), %s)
                            """,
                            (
                                username,
                                new_user_password,
                                new_user_role,
                            ),
                        )

                        st.success("User created successfully.")
                        st.rerun()

                    except Exception:
                        st.error(
                            "Could not create user. "
                            "Username may already exist."
                        )

            st.divider()

            # UPDATE USER ROLE
            st.subheader("Change User Role")

            other_users = users[
                users["user_id"] != user["user_id"]
            ]

            if not other_users.empty:
                selected_id = st.selectbox(
                    "Select Account",
                    other_users["user_id"].tolist(),
                    format_func=lambda uid: str(
                        other_users.loc[
                            other_users["user_id"] == uid,
                            "username",
                        ].iloc[0]
                    ),
                )

                selected_role = str(
                    other_users.loc[
                        other_users["user_id"] == selected_id,
                        "role",
                    ].iloc[0]
                )

                updated_role = st.selectbox(
                    "Select New Role",
                    ROLES,
                    index=(
                        ROLES.index(selected_role)
                        if selected_role in ROLES else 0
                    ),
                )

                if st.button("Update Role", type="primary"):
                    if updated_role != selected_role:
                        db.execute(
                            """
                            UPDATE users
                            SET role = %s
                            WHERE user_id = %s
                            """,
                            (updated_role, int(selected_id)),
                        )

                        st.success("User role updated.")
                        st.rerun()
                    else:
                        st.info("User already has this role.")

            else:
                st.info("No other user accounts available.")

            st.divider()

            # DELETE USER
            st.subheader("Remove User Access")

            if not other_users.empty:
                delete_id = st.selectbox(
                    "Select Account to Delete",
                    other_users["user_id"].tolist(),
                    format_func=lambda uid: str(
                        other_users.loc[
                            other_users["user_id"] == uid,
                            "username",
                        ].iloc[0]
                    ),
                    key="delete_user_select",
                )

                confirm_delete = st.checkbox(
                    "I confirm permanent account deletion."
                )

                if st.button(
                    "Delete User",
                    disabled=not confirm_delete,
                ):
                    db.execute(
                        """
                        DELETE FROM users
                        WHERE user_id = %s
                        """,
                        (int(delete_id),),
                    )

                    st.success("User account deleted.")
                    st.rerun()
