import json
import os
import hashlib

from .log import *
from . import constants as CONSTS

class Auth:
    def __init__(self):
        pass

    def authenticate_user(self, username, password):
        if not os.path.exists(CONSTS.USERS_DATA_FILENAME):
            LOG_FATAL("Users data not found")
            return False
    
        with open(CONSTS.USERS_DATA_FILENAME, "r") as f:
            users = json.load(f)
    
        if username not in users:
            LOG_WARN("User {} not exist", username)
            return False
    
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        return users[username]["password"] == hashed_password

    def create_user(self, username, password):
        pass

    def get_users():
        pass