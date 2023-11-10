import os
import requests


class UserService:
    def change_password(self, user, new_password, auth_pyrebase):
        try:
            id_token = self._refresh_id_token(user)
            url = "https://identitytoolkit.googleapis.com/v1/accounts:update?key=" + os.environ.get('API_KEY')
            headers = {"Content-Type": "application/json"}
            data = {
                "idToken": id_token,
                "password": new_password,
                "returnSecureToken": True
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["refreshToken"], response.json()["idToken"]
            else:
                raise Exception(f"Failed to change password: {response.content}")
        except Exception as e:
            print(f"Error: {e}")
            return None, None

    def delete_account(self, user, db):
        try:
            id_token = self._refresh_id_token(user)
            url = "https://identitytoolkit.googleapis.com/v1/accounts:delete?key=" + os.environ.get('API_KEY')
            headers = {"Content-Type": "application/json"}
            data = {
                "idToken": id_token
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                db.reference("users").child(user.user_id).delete()
                return True
            else:
                raise Exception(f"Failed to delete account: {response.content}")
        except Exception as e:
            print(f"Error: {e}")
            return False

    def _refresh_id_token(self, user):
        try:
            url = "https://securetoken.googleapis.com/v1/token?key=" + os.environ.get('API_KEY')
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "refresh_token",
                "refresh_token": user.refresh_token,
            }
            response = requests.post(url, headers=headers, data=data)
            return response.json()["id_token"]
        except Exception as e:
            print(f"Error: {e}")
            return None
