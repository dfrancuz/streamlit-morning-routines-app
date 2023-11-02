# Morning Routines Application using Streamlit

Jumpstart your day with ease! The Morning Routines Application is your personal morning assistant, offering task management, AI-powered interaction, weather updates, currency exchange rates, and more. Organize your daily routine, set tasks, and receive weather updates, all in one convenient tool.

- ✅ **Task Management**: Plan your day by adding and tracking tasks.
- 🗣️ **AI-Powered Assistance**: Interact with the app using voice commands.
- 🌦️ **Weather Updates**: Stay informed about current weather conditions.
- 💱 **Currency Exchange Rates**: Keep an eye on exchange rates for your financial planning.
- 📚 **Task History**: Review your task history to see which tasks you completed on previous days.

Make your mornings productive and enjoyable with this all-in-one app. Try it yourself!

## Instalation Guide
Follow these steps to install and run Morning Routines Application on your local machine:
1. **Clone the Repository**
   - First, you need to clone the project to your local machine. You can do this by running the following command in your terminal: `git clone https://github.com/dfrancuz/streamlit-morning-routines-app.git`
   - Navigate into the project directory: `cd streamlit-morning-routines-app`

2. **Setup (Optional)**
   - It's recommended to use a virtual environment to keep the dependencies used by this project separate from your other Python projects.
   - If you're using [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/), you can create a new environment with the following command: `conda create --name myenv`
   - Activate the environment using: `conda activate myenv`

3. **Prerequisites**
   - Ensure you have the following [prerequisites](https://github.com/dfrancuz/streamlit-morning-routines-app/blob/main/requirements.txt) installed in your python environment.
   - If not, in your Command Prompt or terminal, navigate to the project directory and type the following command: `pip install -r requirements.txt`

4. **Setup API Keys and Firebase**
   - This application uses [Firebase](https://firebase.google.com/) for data storage and APIs for [weather](https://openweathermap.org/) updates and [currency](https://app.currencyapi.com/login) exchange. You need to set up your own API keys and Firebase credentials before running the application. For more information on how to set up and connect Firebase with your Streamlit app, please visit this [link](https://firebase.google.com/docs/auth/admin).
   - Create a `serviceAccountKey.json` file with your Firebase service account key and place it in the root directory of the project.
   - Set up the following environment variables with your own values:
     
      | Environment Variable |<div align="center"> Description </div> |
      | --- | --- |
      | `DATABASE_URL` | The URL of your Firebase Realtime Database. |
      | `API_KEY` | Your Firebase API key. |
      | `AUTH_DOMAIN` | Your Firebase auth domain. |
      | `BASE_URL` | The URL of your Firebase project. |
      | `PROJECT_ID` | Your Firebase project ID. |
      | `STORAGE_BUCKET` | Your Firebase storage bucket. |
      | `MESSAGING_SENDER_ID` | Your Firebase messaging sender ID. |
      | `APP_ID` | Your Firebase app ID. |
      | `CURRENCY_API_KEY` | Your API key for the currency exchange service. |
      | `CURRENCY_BASE_URL` | The base URL of the currency exchange service. |
      | `WEATHER_API_KEY` | Your API key for the weather service. |
      | `WEATHER_BASE_URL` | The base URL of the weather service. |

5. **Run the Application**
   - After setting up your API keys and Firebase credentials, you can run the application by executing the following command in your terminal: `streamlit run Home.py`
   - Once the application is running, you should see a display similar to [this](https://i.imgur.com/mB7rNVv.png).
  
