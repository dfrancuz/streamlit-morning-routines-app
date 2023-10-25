import streamlit as st

st.set_page_config(
    page_title="About",
    page_icon="💡",
)

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title('About')

local_css("style/style_about.css")

st.markdown("""
<div id="about">
<h1>Welcome to the Morning Routine App!</h1>

<p>This app is designed to help you start your day on the right foot. It's your personal assistant in the morning, providing you with all the information you need to kickstart your day.</p>

<p>Here are some of the features of this app:</p>

<ul>
<li><strong>Task Management</strong>: Add your tasks for the day and keep track of what needs to be done. It's a simple and effective way to manage your daily tasks.</li>

<li><strong>AI-Powered Assistance</strong>: Enhances the functionality of the app by allowing you to interact with it in a conversational manner. Just speak your tasks or queries, and the AI will handle the rest, making the use of the app as easy as having a chat.</li>
            
<li><strong>Task History</strong>: Have a retrospective view on your tasks. Application automatically records your past tasks and their completion status, offering historical perspective on your productivity.</li>
            
<li><strong>Weather Updates</strong>: Stay updated with the current weather conditions. Whether it's sunny, rainy, or cloudy outside, you'll know before you step out.</li>

<li><strong>Currency Exchange Rates</strong>: Keep track of the current currency exchange rates. Whether you're planning a trip or doing some financial planning, this feature will come in handy.</li>
</ul>

<p>This app is built with a lot of love and I hope it helps you have a productive and wonderful day! If you have any questions or suggestions, please feel free to contact me.</p>
</div>
""", unsafe_allow_html=True)
