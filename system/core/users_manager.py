import os
import json
from enum import Enum
import uuid
import bcrypt
from typing import Optional, Dict, List

from . import constants as CONSTS
from .log import *

class UserPrivilege(Enum):
    DEVELOPER = "developer"
    ADMIN = "admin"
    GUEST = "guest"

class User:
    def __init__(self, username, password, privilege: UserPrivilege = UserPrivilege.GUEST):
        self.user_id = str(uuid.uuid4())
        self.username = username
        self.password = self._hash_password(password)
        self.user_path_root = os.path.join(CONSTS.USERS_PATH, username)
        self.privilege = privilege
    
    @staticmethod
    def _hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_json(self) -> Dict:
        return {
            "id": self.user_id,
            "username": self.username,
            "password": self.password,
            "path_root": self.user_path_root,
            "privilege": self.privilege.value
        }

class UsersManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UsersManager, cls).__new__(cls)
            cls._instance.__initialized = False
        return cls._instance
    
    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        
        self.users: List[Dict] = []
        self.users_data_file = CONSTS.USERS_DATA_FILENAME
        
        os.makedirs(CONSTS.USERS_PATH, exist_ok=True)
        
        if not os.path.exists(self.users_data_file):
            with open(self.users_data_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
            LOG_INFO("Users data file was created")
        else:
            self._load_users()
    
    def _load_users(self):
        try:
            with open(self.users_data_file, "r", encoding="utf-8") as f:
                self.users = json.load(f)
                if not isinstance(self.users, list):
                    self.users = []
                LOG_INFO(f"Loaded {len(self.users)} users")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            LOG_ERROR(f"Error loading users: {e}")
            self.users = []

    def _save_users(self):
        try:
            with open(self.users_data_file, "w", encoding="utf-8") as f:
                json.dump(self.users, f, indent=4)
            return True
        except Exception as e:
            LOG_ERROR(f"Error saving users: {e}")
            return False
    
    def create_user(self, username, password, privilege: UserPrivilege = UserPrivilege.GUEST):
        if any(user['username'] == username for user in self.users):
            LOG_ERROR(f"User '{username}' already exists")
            return False

        user = User(username, password, privilege)
        self.users.append(user.to_json())
        
        if self._save_users():
            LOG_INFO(f"User '{username}' created successfully")
            return True
        
        LOG_ERROR(f"Error creating user '{username}'")
        return False

    def authenticate_user(self, username, password):
        user_data = next((user for user in self.users if user['username'] == username), None)
        
        if user_data is None:
            LOG_WARN(f"User '{username}' not found")
            return None
        
        if not bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
            LOG_WARN(f"Invalid password for user '{username}'")
            return None
        
        LOG_INFO(f"User '{username}' authenticated successfully")
        return user_data

    def remove_user(self, user_id_or_username):
        initial_count = len(self.users)
        self.users = [user for user in self.users 
                     if user['id'] != user_id_or_username 
                     and user['username'] != user_id_or_username]
        
        if len(self.users) < initial_count:
            if self._save_users():
                LOG_INFO(f"User '{user_id_or_username}' removed successfully")
                return True
        
        LOG_ERROR(f"User '{user_id_or_username}' not found")
        return False

    def get_users(self):
        return self.users.copy()

    def get_user(self, user_id_or_username):
        return next((user for user in self.users 
                    if user['id'] == user_id_or_username 
                    or user['username'] == user_id_or_username), None)