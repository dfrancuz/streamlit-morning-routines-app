import os
import pyrebase
import pandas as pd
import firebase_admin
import streamlit as st
from datetime import datetime
from classes.user import User
from classes.task import Task
from classes.auth_service import AuthService
from classes.user_service import UserService
from classes.task_service import TaskService
from firebase_admin import credentials, db
from modules.speech_recognition_module import add_task_via_voice
from modules.APIs_module import get_forecast, get_exchange_rate

st.set_page_config(
    page_title="Home",
    page_icon="🏠",
)

def initialize_firebase():
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
    return auth_pyrebase, db

auth_pyrebase, db = initialize_firebase()
auth_service = AuthService()
user_service = UserService()
task_service = TaskService()

def authenticate(auth_pyrebase, db):
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
                user = User(name, email, username, password)
                if username !='' and name !='':
                    success, error_message = auth_service.sign_up(user, auth_pyrebase, db)
                    if success:
                        st.session_state["authentication_status"] = True
                        st.session_state["name"] = user.name
                        st.session_state["user_id"] = user.user_id
                        st.session_state["refresh_token"] = user.refresh_token
                        st.session_state["rerun"] = True
                        st.session_state['loggedin'] = True
                        st.session_state["view"] = "main_page"
                    else:
                        st.warning(error_message)
                else:
                    success, error_message = auth_service.sign_in(user, auth_pyrebase, db)
                    if success:
                        st.session_state["authentication_status"] = True
                        st.session_state["name"] = user.name
                        st.session_state["user_id"] = user.user_id
                        st.session_state["refresh_token"] = user.refresh_token
                        st.session_state["rerun"] = True
                        st.session_state['loggedin'] = True
                        st.session_state["view"] = "main_page"
                    else:
                        st.warning(error_message)

left_column, middle_left, middle_right ,right_column = st.columns([2,1,4,4])

def main_page():
    user_id = st.session_state.get("user_id", None)
    
    if "user_id" is None:
        st.warning("Please sign in to view this page.")
        return
    
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
            new_task = Task(task, description, duration)
            task_service.add_task(new_task, date_ref, ref, current_date)
            new_task_df = pd.DataFrame({'Task': [new_task.task], 
                                        'Description': [new_task.description], 
                                        'Estimated Time (min)': [new_task.duration], 
                                        'Status': [new_task.status]})
            st.session_state.df = pd.concat([st.session_state.df, new_task_df], ignore_index=True)
            st.session_state[f'status_{len(st.session_state.df) - 1}'] = new_task.status
            st.success(f"Task '{new_task.task}' added to your morning routine and realtime database!")
    
    automate_button_pressed = st.button("Add via Voice")

    if automate_button_pressed:
        new_task_data = add_task_via_voice()
        if new_task_data is not None:
            task_name, task_description, task_duration = new_task_data['Task'], new_task_data['Description'], new_task_data['Estimated Time (min)']
            new_task = Task(task_name, task_description, task_duration)
            task_service.add_task(new_task, date_ref, ref, current_date)
            new_task_df = pd.DataFrame({'Task': [new_task.task], 
                                        'Description': [new_task.description], 
                                        'Estimated Time (min)': [new_task.duration], 
                                        'Status': [new_task.status]})
            st.session_state.df = pd.concat([st.session_state.df, new_task_df], ignore_index=True)
            st.session_state[f'status_{len(st.session_state.df) - 1}'] = new_task.status
            st.success(f"Task '{new_task.task}' added to your morning routine and realtime database!")

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
                                task = Task(st.session_state.df.loc[i, 'Task'], 
                                            st.session_state.df.loc[i, 'Description'], 
                                            st.session_state.df.loc[i, 'Estimated Time (min)'], 
                                            status, 
                                            st.session_state.df.loc[i, 'Key'], 
                                            st.session_state.df.loc[i, 'Date'])
                                task_service.change_status(task, new_status, ref)
                                st.session_state.df.loc[i, 'Status'] = new_status
                                st.rerun()

                            remove_button = st.button("Remove Task", key=f"remove_task_{i}")
                            if remove_button:
                                task = Task(st.session_state.df.loc[i, 'Task'], 
                                            st.session_state.df.loc[i, 'Description'], 
                                            st.session_state.df.loc[i, 'Estimated Time (min)'], 
                                            status, 
                                            st.session_state.df.loc[i, 'Key'], 
                                            st.session_state.df.loc[i, 'Date'])
                                task_service.remove_task(task, ref)
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
            list_user_tasks()

def show_forecast():
    
    st.sidebar.title("Current Weather")

    city = "Budapest"
    weather_data = get_forecast(city)
    
    temp_row = st.sidebar.columns([1, 1])
    temp_row[0].markdown(f"**{city}**")
    temp_row[1].markdown(f"🌡️ **{weather_data['main']['temp']}°C**")

    temp_row[0].markdown(f"💧 {weather_data['main']['humidity']}%")
    temp_row[1].markdown(f"💨 {weather_data['wind']['speed']} m/s")

def show_exchange_rate(base_currencies, target_currency):
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


def list_user_tasks():
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
            for task in tasks.items():
                task_list.append({
                    'Task': task['task'], 
                    'Description': task['description'],
                    'Time (min)': task['estimated_time'],
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


def show_user_settings():
    col1_settings, col2_settings = st.columns([2,1])
    
    with col1_settings:
        if 'loggedin' in st.session_state and st.session_state['loggedin']:
            if st.button('Back'):
                st.session_state.view = 'main_page'
                st.rerun()
    with col2_settings:
        st.write(f"{st.session_state['name']}'s **Settings Page**")
    
    current_user = User(st.session_state['name'], 
                        None, None, None, 
                        st.session_state["user_id"], 
                        st.session_state["refresh_token"])

    st.subheader("Change Password")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Change Password"):
        if new_password == "" or confirm_password == "":
            st.info("Please fill out both fields.")
        elif new_password != confirm_password:
            st.warning("Fields do not match!")
        elif new_password == confirm_password:
            refresh_token, id_token = user_service.change_password(current_user, new_password, auth_pyrebase)
            if refresh_token and id_token:
                st.session_state["refresh_token"] = refresh_token
                st.session_state["id_token"] = id_token
                st.success("Password changed successfully.")
            else:
                st.error("Failed to change password.")
    
    st.subheader("Delete Account")
    confirmation = st.text_input("Type 'DELETE' to confirm", type="password")
    if confirmation == "DELETE" and st.button("Delete Account"):
        if user_service.delete_account(current_user, db):
            st.success("Account deleted successfully.")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.view = 'sign_in_page'
            st.rerun()
        else:
            st.error("Failed to delete account.")

def app():
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = False

    if not st.session_state["authentication_status"]:
        authenticate(auth_pyrebase, db)
    elif "view" in st.session_state and st.session_state["view"] == 'other_dates':
        list_user_tasks()
    elif "view" in st.session_state and st.session_state["view"] == 'settings':
        show_user_settings()
    elif "view" in st.session_state and st.session_state["view"] == 'sign_in_page':
        authenticate(auth_pyrebase, db)
    else:
        main_page()
    
    if "rerun" in st.session_state and st.session_state["rerun"]:
        st.session_state["rerun"] = False
        st.rerun()

    show_forecast()
    show_exchange_rate(['EUR', 'USD', 'CHF'], 'HUF')

if __name__ == "__main__":
    app()