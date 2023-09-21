import streamlit as st
from streamlit_authenticator import Authenticate
import yaml
from yaml.loader import SafeLoader

def main_page():
    st.title("Morning Routine Planner")

with open('info.yml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    st.title("Welcome! 👋")
    st.write("Please **Sign In** to continue...")

name, authentication_status, username = authenticator.login('Authentication', 'main')

left_column, middle_left, middle_right ,right_column = st.columns(4)
if st.session_state["authentication_status"]:
    with left_column:
        authenticator.logout('Sign Out', 'main')
    with right_column: 
        st.write(f'Welcome *{st.session_state["name"]}*')
    main_page()
elif st.session_state["authentication_status"] == False:
    st.error('Username or password is incorrect')
elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
