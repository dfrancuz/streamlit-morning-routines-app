import os
import requests

class User:
    def __init__(self, name, email, username, password, user_id=None, refresh_token=None):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.user_id = user_id
        self.refresh_token = refresh_token

    def sign_in(self, auth_pyrebase, db):
        try:
            user = auth_pyrebase.sign_in_with_email_and_password(self.email, self.password)
            self.user_id = user["localId"]
            self.refresh_token = user['refreshToken']
            user_data = db.reference("users").child(self.user_id).get()
            self.name = user_data['name']
            return True, ""
        except Exception as e:
            error_message = str(e)
            #print(f"Unexpected error: {str(e)}")
            if "INVALID_LOGIN_CREDENTIALS" in error_message:
                return False, "You entered wrong credentials, or you don't have an account with this email."
            elif "INVALID_EMAIL" in error_message:
                return False, "Please enter valid email."
            else:
                return False, "An error occurred during sign up."

    def sign_up(self, auth_pyrebase, db):
        try:
            user = auth_pyrebase.create_user_with_email_and_password(self.email, self.password)
            data = {"name": self.name, "username": self.username}
            db.reference("users").child(user["localId"]).set(data)
            self.user_id = user["localId"]
            self.refresh_token = user['refreshToken']
            return True, ""
        except Exception as e:
            error_message = str(e)
            #print(f"Unexpected error: {str(e)}")
            if "EMAIL_EXISTS" in error_message:
                return False, "The email already exists. Please sign in!"
            else:
                return False, "An error occurred during sign up."
    
    def change_password(self, new_password, auth_pyrebase):
        try:
            id_token = self.refresh_id_token()
            url = "https://identitytoolkit.googleapis.com/v1/accounts:update?key=" + os.environ.get('API_KEY')
            headers = {"Content-Type": "application/json"}
            data = {
                "idToken": id_token,
                "password": new_password,
                "returnSecureToken": True
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return True
            else:
                raise Exception(f"Failed to change password: {response.content}")
        except Exception as e:
            print(f"Error: {e}")
            return False

    def delete_account(self, db):
        try:
            id_token = self.refresh_id_token()
            url = "https://identitytoolkit.googleapis.com/v1/accounts:delete?key=" + os.environ.get('API_KEY')
            headers = {"Content-Type": "application/json"}
            data = {
                "idToken": id_token
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                db.reference("users").child(self.user_id).delete()
                return True
            else:
                raise Exception(f"Failed to delete account: {response.content}")
        except Exception as e:
            print(f"Error: {e}")
            return False

    def refresh_id_token(self):
        try:
            url = "https://securetoken.googleapis.com/v1/token?key=" + os.environ.get('API_KEY')
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            }
            response = requests.post(url, headers=headers, data=data)
            return response.json()["id_token"]
        except Exception as e:
            print(f"Error: {e}")
            return None