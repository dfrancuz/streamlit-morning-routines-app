import streamlit as st
import os

# Set Streamlit page configuration
st.set_page_config(
    page_title="Contact",
    page_icon="📫",
)

# Function to load local CSS file for page design
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style/style_contact.css")

st.title('Contact Form')

formsubmit_url = os.environ.get("FORMSUBMIT_URL")

contact_form = f"""
<form action="{formsubmit_url}" method="POST">
     <input type="text" name="name" placeholder="Full Name" required>
     <input type="email" name="email" placeholder="Email Address" required>
     <input type="text" name="topic" placeholder="Topic Name">
     <textarea name="message" placeholder="Your message here..."></textarea>
     <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)
