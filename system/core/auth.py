from .users_manager import UsersManager
from .log import *

class Auth:
    def __init__(self):
        self.users_manager = UsersManager()
    
    def authenticate_user(self, username, password):
        user_data = self.users_manager.authenticate_user(username, password)
        return user_data is not None