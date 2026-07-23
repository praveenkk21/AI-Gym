import streamlit as st
from services.persistence.exercise_repository import (
    create_user,
    get_user,
    verify_user,
    get_or_create_google_user,
)


def _google_configured() -> bool:
    try:
        return (
            hasattr(st, "login")
            and hasattr(st, "secrets")
            and "auth" in st.secrets
        )
    except Exception:
        return False


def render_footer():
    st.markdown(
        """
        <style>
        .aigym-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: #0A0D14;
            border-top: 1px solid rgba(255,255,255,0.07);
            padding: 10px 0;
            text-align: center;
            font-size: 13px;
            color: rgba(255,255,255,0.4);
            z-index: 9999;
            font-family: 'AdobeClean', sans-serif;
        }
        .aigym-footer a {
            color: rgba(255,255,255,0.65);
            text-decoration: none;
            font-weight: 500;
        }
        .aigym-footer a:hover { color: #fff; }
        </style>
        <div class="aigym-footer">
            Created by <a href="https://www.linkedin.com/in/praveenkk21" target="_blank">Praveen</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_wall() -> bool:
    if st.session_state.get("user_id") is not None:
        return True

    # handle Streamlit's native OAuth callback
    if _google_configured() and hasattr(st, "user") and st.user.is_logged_in:
        google_id = getattr(st.user, "sub", None) or st.user.email
        email = st.user.email or ""
        name = getattr(st.user, "name", None) or email.split("@")[0]
        user = get_or_create_google_user(google_id, email, name)
        st.session_state["username"] = user["username"]
        st.session_state["user_id"] = user["id"]
        st.rerun()

    st.markdown(
        """
        <style>
        .login-hero {
            text-align: center;
            padding: 2.5rem 0 1.5rem;
        }
        .login-hero .logo { font-size: 3rem; line-height: 1; }
        .login-hero h1 {
            font-size: 2rem !important;
            font-weight: 700 !important;
            margin: 0.4rem 0 0.25rem !important;
            letter-spacing: -0.5px;
        }
        .login-hero p {
            color: rgba(255,255,255,0.45);
            font-size: 0.95rem;
            margin: 0;
        }
        .login-divider {
            display: flex;
            align-items: center;
            gap: 10px;
            margin: 1.2rem 0;
            color: rgba(255,255,255,0.25);
            font-size: 12px;
        }
        .login-divider::before,
        .login-divider::after {
            content: '';
            flex: 1;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        </style>
        <div class="login-hero">
            <div class="logo">💪</div>
            <h1>bAIreps</h1>
            <p>AI-powered gym coach — track every rep, perfect every set</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

        if _google_configured():
            st.markdown('<div class="login-divider">or</div>', unsafe_allow_html=True)
            if st.button("Continue with Google", use_container_width=True, key="google_login"):
                st.login("google")

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

        if _google_configured():
            st.markdown('<div class="login-divider">or</div>', unsafe_allow_html=True)
            if st.button("Continue with Google", use_container_width=True, key="google_register"):
                st.login("google")

    render_footer()
    return False
