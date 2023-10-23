import streamlit as st
import os

st.set_page_config(
    page_title="Contact",
    page_icon="📫",
)

st.title('Contact Form')

formsubmit_url = os.environ.get("FORMSUBMIT_URL")

contact_form = f"""
<form action="{formsubmit_url}" method="POST">
     <input type="text" name="name" placeholder="Full Name" required>
     <input type="email" name="email" placeholder="Email Address" required>
     <textarea name="message" placeholder="Your message"></textarea>
     <button type="submit">Send</button>
</form>
"""

st.markdown(contact_form, unsafe_allow_html=True)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style/style.css")