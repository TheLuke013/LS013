import os
import json

from . import constants as CONSTS
from .log import *

class UsersManager:
    def __init__(self):
        if not os.path.exists(CONSTS.USERS_DATA_FILENAME):
            with open(CONSTS.USERS_DATA_FILENAME, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
            LOG_INFO("Users data file was created")
        else:
            with open(CONSTS.USERS_DATA_FILENAME, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict) and len(data) == 0:
                        LOG_INFO("Users data status: empty")
                    else:
                        LOG_INFO("Users data status: has data")
                        
                except json.JSONDecodeError:
                    LOG_ERROR("Users data file has invalid JSON")
