import importlib
import sys
from types import ModuleType
from typing import Optional, Tuple

class AppLauncher:
    @staticmethod
    def launch_app(app: 'App') -> Tuple[bool, str]:
        try:
            module = AppLauncher._import_app_module(app) 
            app_class = AppLauncher._get_main_class(module, app)
            
            app_instance = app_class()
            app_instance.show()
            
            return (True, "Application started successfully")
            
        except Exception as e:
            return (False, f"Failed to start application: {str(e)}")

    @staticmethod
    def _import_app_module(app: 'App') -> ModuleType:
        try:
            if app.manifest.package not in sys.modules:
                module = importlib.import_module(app.manifest.package)
            else:
                module = importlib.reload(sys.modules[app.manifest.package])
            return module
        except ImportError as e:
            raise RuntimeError(f"Failed to import module {app.manifest.package}: {str(e)}")

    @staticmethod
    def _get_main_class(module: ModuleType, app: 'App') -> type:
        try:
            app_class = getattr(module, app.manifest.main_class)
            if not isinstance(app_class, type):
                raise TypeError(f"{app.manifest.main_class} is not a valid class")
            return app_class
        except AttributeError:
            raise RuntimeError(f"Main class '{app.manifest.main_class}' not found in module")