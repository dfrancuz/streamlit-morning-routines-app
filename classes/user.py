class User:
    def __init__(self, name, email, username, password, user_id=None, refresh_token=None):
        # Initialize the User class with the provided parameters
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.user_id = user_id
        self.refresh_token = refresh_token
