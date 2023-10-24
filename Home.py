import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, db
import pyrebase
import os
import pandas as pd
import speech_recognition as sr
import re
import pyttsx3
from datetime import datetime

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
                    #st.success("🛑 Recording stopped")
                break
            except sr.WaitTimeoutError:
                if not is_recording:
                    is_recording = True
    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

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
            for key in list(st.session_state.keys()):
                if key == 'df':
                    st.session_state[key] = pd.DataFrame()
                else:
                    st.session_state[key] = None
            st.experimental_rerun()

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

    automate_button_pressed = st.button("Automate")

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

            response_status.markdown(f"**{question}** {icons[i]}")

        if task_duration is not None:
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
        
    st.subheader("Your Morning Routine:")
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
                                st.experimental_rerun()

                            remove_button = st.button("Remove Task", key=f"remove_task_{i}")
                            if remove_button:
                                task_key = st.session_state.df.loc[i, 'Key']
                                task_date = st.session_state.df.loc[i, 'Date']
                                ref.child(f'{task_date}/{task_key}').delete()
                                st.session_state.df.drop(index=i, inplace=True)
                                st.experimental_rerun()
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