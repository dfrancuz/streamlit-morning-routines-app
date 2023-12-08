import re
import pyttsx3
import streamlit as st
import speech_recognition as sr

# Function uses text-to-speech to vocalize the provided text
def _speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function transcribes speech from input voice
def _transcribe_speech(prompt=None):
    r = sr.Recognizer()
    is_recording = False

    # Create a microphone instance
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        if prompt:
            st.write(prompt)

        audio = None
        # Listen for an audio
        while True:
            try:
                with st.spinner("Listening..."):
                    audio = r.listen(source, timeout=4)
                break
            except sr.WaitTimeoutError:
                if not is_recording:
                    is_recording = True
    try:
        # Use Google Speech Recognition to transcribe the audio to text
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Function that adds a task via voice input
def add_task_via_voice():
    questions = ["What is your task name?", "How long will it take?", "Can you describe the task?"]
    responses = []
    task_duration = None

    for i, question in enumerate(questions):
        _speak(question)
        response = _transcribe_speech()
        # Process the response based on the question index
        if response:
            if i == 1:
                # Extract numeric duration from this response
                match = re.search(r'\d+', response)
                if match:
                    task_duration = int(match.group())
                else:
                    task_duration = None
            else:
                responses.append(response)
        else:
            # print("Could not understand the response. Please try again.")
            return None

    if len(responses) == 2 and task_duration is not None:
        task_name, task_description = responses
        return {
            'Task': task_name,
            'Description': task_description,
            'Estimated Time (min)': task_duration,
            'Status': 'Not Started'
        }
    else:
        # print("Could not understand one or more of your responses. Please try again.")
        return None
