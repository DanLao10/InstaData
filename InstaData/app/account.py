import streamlit as st
import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
import requests

FIREBASE_API_KEY = st.secrets.firebase_credentials.FIREBASE_API_KEY

def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    resp = requests.post(url, json={
        "email": email,
        "password": password,
        "returnSecureToken": True
    })
    if resp.status_code != 200:
        # Wrong password / user not found / disabled, etc.
        raise ValueError(resp.json().get("error", {}).get("message", "LOGIN_FAILED"))
    return resp.json()  # contains idToken, email, localId (uid), etc.

def get_firebase_app():
    cred = credentials.Certificate("st.instadata-e06b8-afda9d948eed.json")
    try:
        return firebase_admin.get_app()
    except ValueError:
        return firebase_admin.initialize_app(cred)

def app():
    get_firebase_app()
    st.title("Welcome to :violet[InstaData]!")
    # choice = st.selectbox("Login/Signup", ["Login", "Sign Up"])

    st.markdown("""
    :violet[InstaData helps you quickly get insights from your data!].
    
    💬 Chat with Structured Data Forget complex queries.
    
    📊 Automatic Visualizations & Trend Spotting Instantly see the story your data is telling. 
    
    🧠 Deep Business Insights & Root Causes Go beyond the what and understand the why. 
    
    🐍 Transparent Python Code Generation Trust and verify every result. 

    """)

    # initialize st.session_state.username and st.session_state.useremail
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "useremail" not in st.session_state:
        st.session_state.useremail = ""



    def f():
        try:
            # This will raise if password is wrong, etc.
            data = firebase_login(email, password)   # NEW: verifies the password
            # On success, Firebase returns user info; use that to set your state:
            # st.session_state.username = data.get("localId", "")  # uid
            st.session_state.useremail = data.get("email", "")
            st.session_state.password = data.get("password", "")
            # Optionally keep token if you need it later:
            # st.session_state.id_token = data.get("idToken")

            st.session_state.signedout = True
            st.session_state.signout = True

            st.success("Login Successful")
            st.button("Sign Out", on_click=t)
        except Exception:
            pass
            # st.warning("Login Failed")  # wrong password / no such user, etc.

    def t():
        st.session_state.signedout = False
        st.session_state.signout = False
        st.session_state.username = ""

    if "signedout" not in st.session_state:
        st.session_state.signedout = False
    if "signout" not in st.session_state:
        st.session_state.signout = False

    if not st.session_state["signedout"]:
        choice = st.radio(label = "", options = ["Login", "Sign Up"], horizontal=True)

        if choice == "Login":
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")

            st.button("Login", on_click=f)
        else:
            email = st.text_input("Enter Your Email Address")
            # username = st.text_input("Enter your unique username")
            password = st.text_input("Please select a Password", type="password")

            if st.button("Create my account"):
                user = auth.create_user(email=email, password=password)
                st.success("Account created successfully!")
                st.markdown("Please login with your email and password")

    # if st.session_state.signout:
    #     st.text("Username: " + st.session_state.username)
    #     st.text("Email: " + st.session_state.useremail)
    #     st.button("Sign Out", on_click=t)
