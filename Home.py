import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db
import pyrebase
import os

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

cred = credentials.Certificate('serviceAccountKey.json')

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.environ.get('DATABASE_URL')
    })

firebaseConfig = {
            'apiKey': os.environ.get('API_KEY'),
            'authDomain': os.environ.get('AUTH_DOMAIN'),
            'databaseURL': os.environ.get('BASE_URL'),
            'projectId': os.environ.get('PROJECT_ID'),
            'storageBucket': os.environ.get('STORAGE_BUCKET'),
            'messagingSenderId': os.environ.get('MESSAGING_SENDER_ID'),
            'appId': os.environ.get('APP_ID')
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth_pyrebase = firebase.auth()

left_column, middle_left, middle_right ,right_column = st.columns(4)

def main_page():
    st.title("Morning Routine Planner")
    with right_column:
        st.write(f"Welcome {st.session_state['name']}!")
    with left_column:
        if st.button("Log Out"):
            for key in list(st.session_state.keys()):
                st.session_state[key] = None
            st.experimental_rerun()

def sign_in():
    with st.form(key='auth_form'):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input('Full Name')
            email = st.text_input('Email')
        with col2:
            username = st.text_input('Username')
            password = st.text_input('Password', type='password')

        if st.form_submit_button('Sign In / Sign Up'):
            if(email =='' or password == ''):
                st.warning('Please enter your email and password.')
            else:
                try:
                    user = auth_pyrebase.sign_in_with_email_and_password(email, password)
                    data = db.reference("users").child(user["localId"]).get()
                    if data is not None:
                        st.session_state["authentication_status"] = True
                        st.session_state["name"] = data['name']
                        st.session_state["rerun"] = True
                except:
                    try:
                        user = auth.get_user_by_email(email)
                        if user is not None or user["email"] == email and user["password"] != password:
                            st.warning('Wrong credentials. Please try again.')
                    except:
                        if(username !='' and name !=''):
                            try:
                                user = auth_pyrebase.create_user_with_email_and_password(email, password)
                                data = {"name": name, "username": username}
                                db.reference("users").child(user["localId"]).set(data)
                                data = db.reference("users").child(user["localId"]).get()
                                if data is not None:
                                    st.session_state["authentication_status"] = True
                                    st.session_state["name"] = data['name']
                                    st.session_state["rerun"] = True
                            except:
                                st.warning('The account already exists! Please try to sign in.')
                        else:
                            st.warning('Please enter your full name and username to create a new account.')

if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = False

if not st.session_state["authentication_status"]:
    sign_in()
else:
    main_page()

if "rerun" in st.session_state and st.session_state["rerun"]:
    st.session_state["rerun"] = False
    st.experimental_rerun()