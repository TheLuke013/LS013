from loguru import logger
import os

from . import constants as CONSTS

class Log:
    _logger = None

    @staticmethod
    def init():
        logger.add(os.path.join(CONSTS.LOGS_PATH, "system_{time}.log"), rotation="500 MB")
        logger.info("Initializing Log System")
        Log._logger = logger
    
    @staticmethod
    def get_logger():
        if Log._logger is None:
            raise Exception("Logger not initialized. Call Log.init() first")
        return Log._logger

def LOG_TRACE(msg, *args):   Log.get_logger().debug(msg, *args)
def LOG_INFO(msg, *args):    Log.get_logger().info(msg, *args)
def LOG_WARN(msg, *args):    Log.get_logger().warning(msg, *args)
def LOG_ERROR(msg, *args):   Log.get_logger().error(msg, *args)
def LOG_FATAL(msg, *args):   Log.get_logger().critical(msg, *args)