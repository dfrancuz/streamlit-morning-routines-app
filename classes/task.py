import streamlit as st
import pandas as pd

class Task:
    def __init__(self, task, description, duration, status='Not Started', key=None, date=None):
        self.task = task
        self.description = description
        self.duration = duration
        self.status = status
        self.key = key
        self.date = date
    
    def add_task(self, date_ref, ref, current_date):
        new_task = {
            'task': self.task,
            'description': self.description,
            'estimated_time': self.duration,
            'status': self.status
        }

        if date_ref.get() is None:
            date_ref.push(new_task)
        else:
            ref.child(current_date).push(new_task)

        new_task_df = pd.DataFrame({'Task': [self.task], 
                                    'Description': [self.description], 
                                    'Estimated Time (min)': [self.duration], 
                                    'Status': [self.status]})
        st.session_state.df = pd.concat([st.session_state.df, new_task_df], ignore_index=True)
        st.session_state[f'status_{len(st.session_state.df) - 1}'] = self.status
        st.success(f"Task '{self.task}' added to your morning routine and realtime database!")

    def remove_task(self, i, ref):
        task_key = self.key
        task_date = self.date
        ref.child(f'{task_date}/{task_key}').delete()
        st.session_state.df.drop(index=i, inplace=True)
        st.rerun()

    def change_status(self, i, new_status, ref):
        task_key = self.key
        task_date = self.date
        ref.child(f'{task_date}/{task_key}').update({'status': new_status})
        st.session_state.df.loc[i, 'Status'] = new_status
        st.rerun()