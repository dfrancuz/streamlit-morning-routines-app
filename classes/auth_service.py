class AuthService:
    def sign_in(self, user, auth_pyrebase, db):
        try:
            user_data = auth_pyrebase.sign_in_with_email_and_password(user.email, user.password)
            user.user_id = user_data["localId"]
            user.refresh_token = user_data['refreshToken']
            db_user_data = db.reference("users").child(user.user_id).get()
            user.name = db_user_data['name']
            return True, ""
        except Exception as e:
            error_message = str(e)
            if "INVALID_LOGIN_CREDENTIALS" in error_message:
                return False, "You entered wrong credentials, or you don't have an account with this email."
            elif "INVALID_EMAIL" in error_message:
                return False, "Please enter valid email."
            else:
                return False, "An error occurred during sign in."

    def sign_up(self, user, auth_pyrebase, db):
        try:
            user_data = auth_pyrebase.create_user_with_email_and_password(user.email, user.password)
            data = {"name": user.name, "username": user.username}
            db.reference("users").child(user_data["localId"]).set(data)
            user.user_id = user_data["localId"]
            user.refresh_token = user_data['refreshToken']
            return True, ""
        except Exception as e:
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                return False, "The email already exists. Please sign in!"
            else:
                return False, "An error occurred during sign up."