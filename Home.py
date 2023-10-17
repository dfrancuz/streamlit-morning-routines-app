import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db
import pyrebase
import os
import pandas as pd
import requests

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


def get_forecast(city: str):
    api_key = os.environ.get("WEATHER_API_KEY")
    base_url = os.environ.get("WEATHER_BASE_URL")
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    return response.json()

def show_forecast():
    
    st.sidebar.title("Current Weather")

    city = "Budapest"
    weather_data = get_forecast(city)
    
    temp_row = st.sidebar.columns([1, 1])
    temp_row[0].markdown(f"**{city}**")
    temp_row[1].markdown(f"🌡️ **{weather_data['main']['temp']}°C**")

    temp_row[0].markdown(f"💧 {weather_data['main']['humidity']}%")
    temp_row[1].markdown(f"💨 {weather_data['wind']['speed']} m/s")

show_forecast()


@st.cache_data
def get_exchange_rate(base_currency, target_currency):
    api_key = os.environ.get("CURRENCY_API_KEY")
    base_url = os.environ.get("CURRENCY_BASE_URL")
    complete_url = f'{base_url}/latest?apikey={api_key}&base_currency={base_currency}'
    response = requests.get(complete_url)
    data = response.json()
    
    if response.status_code == 200:
        if 'data' in data and target_currency in data['data']:
            exchange_rate = data['data'][target_currency]['value']
            #st.session_state.exchange_rate_fetched = True
            return exchange_rate
        else:
            st.sidebar.write('Error: The response does not contain exchange rates.')
            return None
    else:
        if 'error' in data:
            st.sidebar.write('Error: ', data['error'])
        else:
            st.sidebar.write('Error: The response does not contain an error message.')
        return None


left_column, middle_left, middle_right ,right_column = st.columns(4)

def main_page():
    if "user_id" in st.session_state:
        user_id = st.session_state["user_id"]
    
    if 'df' not in st.session_state:
        data = {'Task': [], 'Description': [], 'Estimated Time (min)': [], 'Status': []}
        st.session_state.df = pd.DataFrame(data)

    st.title("Morning Routine Planner")
    with right_column:
        st.write(f"Welcome {st.session_state['name']}!")
    with left_column:
        if st.button("Log Out"):
            st.session_state.clear()
            st.session_state.update({
                'df': pd.DataFrame(),
                'exchange_rates': {},
            })
            st.experimental_rerun()

    ref = db.reference(f'users/{user_id}/tasks')
    tasks = ref.get()

    if tasks is None:
        data = {'Task': [], 'Description': [], 'Estimated Time (min)': [], 'Status': [], 'Key': []}
        st.session_state.df = pd.DataFrame(data)
    else:
        task_list = [{'Task': task['task'], 'Description': task['description'], 'Estimated Time (min)': task['estimated_time'], 'Status': task['status'], 'Key': key} for key, task in tasks.items()]
        st.session_state.df = pd.DataFrame(task_list)

    with st.form(key='task_form'):
        task = st.text_input('Enter Task')
        description = st.text_input("Enter Description")
        duration = st.number_input("Estimated Time (min)", min_value=1)
        submit_button = st.form_submit_button(label='Add Task')

    if submit_button:
        if task != '' and duration > 0:
            new_task = {
                'task': task,
                'description': description,
                'estimated_time': duration,
                'status': 'Not Started'
            }
            ref.push(new_task)
            new_task = pd.DataFrame({'Task': [task], 'Description': [description], 'Estimated Time (min)': [duration], 'Status': ['Not Started']})
            st.session_state.df = pd.concat([st.session_state.df, new_task], ignore_index=True)
            st.session_state[f'status_{len(st.session_state.df) - 1}'] = 'Not Started'
            st.success(f"Task '{task}' added to your morning routine and realtime database!")
    
    st.subheader("Your Morning Routine:")
    if st.session_state.df.empty:
        st.info("No tasks added yet.")
    else:
        for i in range(len(st.session_state.df)):
            if pd.notna(st.session_state.df.loc[i, 'Task']):
                status = st.session_state.df.loc[i, 'Status']
                if status == 'Completed':
                    status_indicator = '✅'
                elif status == 'In Progress':
                    status_indicator = '🔄'
                else:
                    status_indicator = '❌'
                
                with st.expander(f"{status_indicator} {st.session_state.df.loc[i, 'Task']} {st.session_state.df.loc[i, 'Estimated Time (min)']} minutes"):
                    st.markdown(f"**Description:** {st.session_state.df.loc[i, 'Description']}")
                    new_status = st.selectbox('', ['Not Started', 'In Progress', 'Completed'], key=f'status_{i}', index=['Not Started', 'In Progress', 'Completed'].index(status))
                    if new_status != status:
                        task_key = st.session_state.df.loc[i, 'Key']
                        ref.child(task_key).update({'status': new_status})
                        st.session_state.df.loc[i, 'Status'] = new_status
                        st.experimental_rerun()
                    
                    remove_button = st.button("Remove Task", key=f"remove_task_{i}")
                    
                    if remove_button:
                        task_key = st.session_state.df.loc[i, 'Key']
                        ref.child(task_key).delete()
                        st.session_state.df.drop(index=i, inplace=True)
                        st.experimental_rerun()

        st.session_state.df['Estimated Time (min)'] = pd.to_numeric(st.session_state.df['Estimated Time (min)'], errors='coerce')
        total_time = st.session_state.df.loc[st.session_state.df['Status'] != 'Completed', 'Estimated Time (min)'].sum()
        st.write(f"Total Estimated Time for Incomplete Tasks: {str(total_time)} minutes")

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
                        st.session_state["user_id"] = user["localId"]
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


base_currencies = ['EUR', 'USD', 'CHF']
target_currency = 'HUF'

if "exchange_rates" not in st.session_state:
    st.session_state.exchange_rates = {}

button_placeholder = st.sidebar.empty()

if not all(base_currency in st.session_state.exchange_rates for base_currency in base_currencies):
    button = button_placeholder.button("Check Currency Exchange")

    if button:
        button_placeholder.empty()

        with st.sidebar.expander("Exchange Rates"):
            for base_currency in base_currencies:
                rate = get_exchange_rate(base_currency, target_currency)
                if rate is not None:
                    formatted_rate = format(rate, '.2f')
                    st.session_state.exchange_rates[base_currency] = rate
                    st.write(f'**{base_currency}** to **{target_currency}**: {formatted_rate}')
else:
    with st.sidebar.expander("Exchange Rates"):
        for base_currency in base_currencies:
            rate = st.session_state.exchange_rates[base_currency]
            formatted_rate = format(rate, '.2f')
            st.write(f'**{base_currency}** to **{target_currency}**: {formatted_rate}')