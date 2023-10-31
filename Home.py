import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db
import pyrebase
import os
import pandas as pd
import requests
from datetime import datetime
import speech_recognition as sr
import re
import pyttsx3

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

def transcribe_speech(prompt=None):
    r = sr.Recognizer()
    is_recording = False

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        if prompt:
            st.write(prompt)

        audio = None
        while True:
            try:
                with st.spinner("Listening..."):
                    audio = r.listen(source, timeout=4)
                break
            except sr.WaitTimeoutError:
                if not is_recording:
                    is_recording = True
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

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


left_column, middle_left, middle_right ,right_column = st.columns([2,1,4,4])

def list_tasks():
    user_id = st.session_state["user_id"]

    col3, col4 = st.columns([2,1])
    
    with col3:
        if 'loggedin' in st.session_state and st.session_state['loggedin']:
            if st.button('Back'):
                st.session_state.view = 'main_page'
                st.rerun()
    with col4:
        st.write(f"{st.session_state['name']}'s **Task History**")

    col1, col2 = st.columns([0.35,2])
    with col1:
        selected_date = st.date_input('Select a date', value=datetime.today())
    with col2:
        st.write('')
        st.write('')
        show_tasks_button = st.button('Show tasks')

    if show_tasks_button:
        ref = db.reference(f'users/{user_id}/tasks/{selected_date.strftime("%Y-%m-%d")}')
        tasks = ref.get()

        if tasks is None:
            st.info("No tasks for the selected date.")
        else:
            task_list = []
            for key, task in tasks.items():
                task_list.append({
                    'Task': task['task'], 
                    'Description': task['description'],
                    'Time': task['estimated_time'],
                    'Status': task['status']
                })
            df = pd.DataFrame(task_list)

            status_icons = {
                'Completed': '✅',
                'In Progress': '🔄',
                'Not Started': '❌'
            }
            df['Status'] = df['Status'].map(status_icons)

            st.dataframe(df, use_container_width=True)


def refresh_id_token(refresh_token):
    url = "https://securetoken.googleapis.com/v1/token?key=" + os.environ.get('API_KEY')
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()["id_token"]


def show_user_settings():
    col1_settings, col2_settings = st.columns([2,1])
    
    with col1_settings:
        if 'loggedin' in st.session_state and st.session_state['loggedin']:
            if st.button('Back'):
                st.session_state.view = 'main_page'
                st.rerun()
    with col2_settings:
        st.write(f"{st.session_state['name']}'s **Settings Page**")
     
    st.subheader("Change Password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Change Password"):
        if new_password == "" or confirm_password == "":
            st.info("Please fill out both fields.")
        elif new_password == confirm_password:
            if "refresh_token" in st.session_state:
                id_token = refresh_id_token(st.session_state["refresh_token"])
                url = "https://identitytoolkit.googleapis.com/v1/accounts:update?key=" + os.environ.get('API_KEY')
                headers = {"Content-Type": "application/json"}
                data = {
                    "idToken": id_token,
                    "password": new_password,
                    "returnSecureToken": True
                }
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    st.success("Password changed successfully.")
                else:
                    st.error(f"Failed to change password: {response.content}")
            else: 
                st.warning("Please sign in again.")
    
    st.subheader("Delete Account")
    confirmation = st.text_input("Type 'DELETE' to confirm", type="password")
    if confirmation:
        st.warning("Warning: Deleting your account is irreversible.")
        if confirmation == "DELETE" and st.button("Delete Account"):
            if "refresh_token" in st.session_state:
                id_token = refresh_id_token(st.session_state["refresh_token"])
                url = "https://identitytoolkit.googleapis.com/v1/accounts:delete?key=" + os.environ.get('API_KEY')
                headers = {"Content-Type": "application/json"}
                data = {
                    "idToken": id_token
                }
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    st.success("Account deleted successfully.")
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state.view = 'sign_in_page'
                    st.rerun()
                else:
                    st.error(f"Failed to delete account: {response.content}")
            else: 
                st.warning("Please sign in again.")


def main_page():
    if "user_id" in st.session_state:
        user_id = st.session_state["user_id"]
    
    if 'df' not in st.session_state:
        data = {'Task': [], 'Description': [], 'Estimated Time (min)': [], 'Status': []}
        st.session_state.df = pd.DataFrame(data)

    st.title("Morning Routine Planner")
    with right_column:
        sub_col1, sub_col2 = st.columns([3,1])
        with sub_col1:
            st.write(f"Welcome {st.session_state['name']}!")
        with sub_col2:
            if st.button("⚙️"):
                st.session_state.view = 'settings'
                st.rerun()
                show_user_settings()
        
    with left_column:
        if st.button("Log Out"):
            st.session_state.clear()
            st.session_state.update({
                'df': pd.DataFrame(),
                'exchange_rates': {},
                'loggedin': False,
            })
            st.rerun()

    current_date = datetime.now().strftime('%Y-%m-%d')
    ref = db.reference(f'users/{user_id}/tasks')
    date_ref = ref.child(current_date)
    tasks = date_ref.get()
    
    if tasks is None:
        data = {'Task': [], 'Description': [], 'Estimated Time (min)': [], 'Status': [], 'Key': []}
        st.session_state.df = pd.DataFrame(data)
    else:
        task_list = []
        for key, task in tasks.items():
            task_list.append({
                'Task': task['task'], 
                'Description': task['description'], 
                'Estimated Time (min)': task['estimated_time'], 
                'Status': task['status'], 
                'Key': key,
                'Date': current_date
            })
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

            if date_ref.get() is None:
                date_ref.push(new_task)
            else:
                ref.child(current_date).push(new_task)

            new_task = pd.DataFrame({'Task': [task], 'Description': [description], 'Estimated Time (min)': [duration], 'Status': ['Not Started']})
            st.session_state.df = pd.concat([st.session_state.df, new_task], ignore_index=True)
            st.session_state[f'status_{len(st.session_state.df) - 1}'] = 'Not Started'
            st.success(f"Task '{task}' added to your morning routine and realtime database!")
    
    questions = ["What is your task name?", "How long will it take?", "Can you describe the task?"]

    automate_button_pressed = st.button("Add via Voice")

    if automate_button_pressed:
        icons = ['🔄', '🔄', '🔄']
        responses = []
        task_duration = None
        
        for i, question in enumerate(questions):
            response_status = st.empty()
            with response_status:
                st.markdown(f"**{question}** {icons[i]}")
            
            speak(question)
            response = transcribe_speech()

            if response:
                icons[i] = '✅'
                if i == 1:
                    match = re.search(r'\d+', response)
                    if match:
                        task_duration = int(match.group())
                    else:
                        task_duration = None
                else:
                    responses.append(response)
                    #st.success("Response captured: " + response)
            else:
                icons[i] = '❌'
                st.warning("Could not understand the response. Please try again.")
                return

            response_status.markdown(f"**{question}** {icons[i]}")

        if len(responses) == 2 and task_duration is not None:
            task_name, task_description = responses
            new_task = {
                'task': task_name,
                'description': task_description,
                'estimated_time': task_duration,
                'status': 'Not Started'
            }
            if date_ref.get() is None:
                date_ref.push(new_task)
            else:
                ref.child(current_date).push(new_task)
                
            new_task = pd.DataFrame({'Task': [task_name], 'Description': [task_description], 'Estimated Time (min)': [task_duration], 'Status': ['Not Started']})
            st.session_state.df = pd.concat([st.session_state.df, new_task], ignore_index=True)
            st.session_state[f'status_{len(st.session_state.df) - 1}'] = 'Not Started'
            st.success(f"Task '{task_name}' added to your morning routine and realtime database!")
        else:
            st.error("Could not understand one or more of your responses. Please try again.")


    st.header("Your Morning Routine")
    if st.session_state.df.empty:
        st.info("No tasks added yet.")
    else:
        for status, status_indicator in [('Completed', '✅'), ('In Progress', '🔄'), ('Not Started', '❌')]:
            st.subheader(f"{status} Tasks:")
            if f"show_{status}" not in st.session_state:
                st.session_state[f"show_{status}"] = True
            show_status = st.checkbox(f"Show {status} Tasks", key=f"show_{status}")
            if show_status:
                tasks_exist = False
                for i in range(len(st.session_state.df)):
                    if pd.notna(st.session_state.df.loc[i, 'Task']) and st.session_state.df.loc[i, 'Status'] == status:
                        tasks_exist = True
                        with st.expander(f"{status_indicator} {st.session_state.df.loc[i, 'Task']} {st.session_state.df.loc[i, 'Estimated Time (min)']} minute(s)"):
                            st.markdown(f"**Description:** {st.session_state.df.loc[i, 'Description']}")
                            new_status = st.selectbox('', ['Not Started', 'In Progress', 'Completed'], key=f'status_{i}', index=['Not Started', 'In Progress', 'Completed'].index(status))
                            if new_status != status:
                                task_key = st.session_state.df.loc[i, 'Key']
                                task_date = st.session_state.df.loc[i, 'Date']
                                ref.child(f'{task_date}/{task_key}').update({'status': new_status})
                                st.session_state.df.loc[i, 'Status'] = new_status
                                st.rerun()

                            remove_button = st.button("Remove Task", key=f"remove_task_{i}")
                            if remove_button:
                                task_key = st.session_state.df.loc[i, 'Key']
                                task_date = st.session_state.df.loc[i, 'Date']
                                ref.child(f'{task_date}/{task_key}').delete()
                                st.session_state.df.drop(index=i, inplace=True)
                                st.rerun()
                if not tasks_exist:
                    st.info("No active tasks in this section.")

        st.session_state.df['Estimated Time (min)'] = pd.to_numeric(st.session_state.df['Estimated Time (min)'], errors='coerce')
        total_time = st.session_state.df.loc[st.session_state.df['Status'] != 'Completed', 'Estimated Time (min)'].sum()

        if total_time > 60:
            hours = total_time // 60
            minutes = total_time % 60
            st.markdown(f"Estimated time for incomplete tasks: **{hours}h {minutes}min**")
        else:
            if(total_time == 1):
                st.markdown(f"Estimated time for incomplete tasks: **{total_time} minute**")
            else:
                st.markdown(f"Estimated time for incomplete tasks: **{total_time} minutes**")

    st.divider()
    task_column1, task_column2 = st.columns([10,2])
    with task_column1:
        st.subheader("Explore your task history by date")
    with task_column2:
        if st.button('Task History'):
            st.session_state.view = 'other_dates'
            st.rerun()
            list_tasks()

def sign_in():
    st.title("Welcome to Morning Routines App")
    st.caption("Please **Sign In** or **Sign Up** to continue.")
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
                    refresh_token = user['refreshToken']
                    st.session_state["refresh_token"] = refresh_token
                    data = db.reference("users").child(user["localId"]).get()
                    if data is not None:
                        st.session_state["authentication_status"] = True
                        st.session_state["name"] = data['name']
                        st.session_state["user_id"] = user["localId"]
                        st.session_state["rerun"] = True
                        st.session_state['loggedin'] = True
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

def app():
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = False

    if not st.session_state["authentication_status"]:
        sign_in()
    elif "view" in st.session_state and st.session_state["view"] == 'other_dates':
        list_tasks()
    elif "view" in st.session_state and st.session_state["view"] == 'settings':
        show_user_settings()
    elif "view" in st.session_state and st.session_state["view"] == 'sign_in_page':
        sign_in()
    else:
        main_page()

app()

if "rerun" in st.session_state and st.session_state["rerun"]:
    st.session_state["rerun"] = False
    st.rerun()

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