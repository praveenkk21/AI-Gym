import streamlit as st
from services.persistence.exercise_repository import create_user, get_user, verify_user


def render_login_wall():
    if st.session_state.get("user_id") is not None:
        return True

    st.title("💪 Baireps - AI fitness coach")
    st.markdown("### Welcome! Please log in or create an account.")

    login_tab, register_tab = st.tabs(["Log In", "Register"])

    with login_tab:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Your username")
            password = st.text_input("Password", type="password", placeholder="Your password")
            submit = st.form_submit_button("Log In", use_container_width=True)

        if submit:
            if not username or not password:
                st.error("Username and password are required.")
                return False
            user = verify_user(username, password)
            if user is None:
                st.error("Invalid username or password.")
                return False
            st.session_state["username"] = user["username"]
            st.session_state["user_id"] = user["id"]
            st.rerun()

    with register_tab:
        with st.form("register_form", clear_on_submit=False):
            new_username = st.text_input("Choose a username", placeholder="Unique username")
            new_password = st.text_input("Choose a password", type="password", placeholder="At least 6 characters")
            confirm_password = st.text_input("Confirm password", type="password", placeholder="Repeat password")
            register = st.form_submit_button("Create Account", use_container_width=True)

        if register:
            if not new_username or not new_password:
                st.error("Username and password are required.")
                return False
            if len(new_password) < 6:
                st.error("Password must be at least 6 characters.")
                return False
            if new_password != confirm_password:
                st.error("Passwords do not match.")
                return False
            if get_user(new_username) is not None:
                st.error("That username is already taken.")
                return False
            user = create_user(new_username, new_password)
            st.session_state["username"] = user["username"]
            st.session_state["user_id"] = user["id"]
            st.rerun()

    return False
