import os
import json
from typing import List

from core.app import App, AppManifest, AppVersion
from core.constants import *
from .log import *

class AppsManager:
    def __init__(self):
        self.apps: List[App] = []
        self.active_apps: List[App] = []
        self.apps_data_file = APPS_DATA_FILENAME
        
        self._load_apps()
        
    def _load_apps(self) -> None:
        try:
            if not os.path.exists(self.apps_data_file) or os.path.getsize(self.apps_data_file) == 0:
                LOG_WARN("Apps registry file not found or empty, creating default...")
                self._create_default_registry()
                return
                
            with open(self.apps_data_file, "r", encoding="utf-8") as f:
                apps_data = json.load(f)
                
                if not isinstance(apps_data, list):
                    raise ValueError("Invalid apps registry format - expected list")
                
                for app_data in apps_data:
                    try:
                        manifest = AppManifest.from_dict(app_data)
                        app = App(manifest)
                        self.apps.append(app)
                    except Exception as e:
                        LOG_ERROR(f"Failed to load app {app_data.get('name')}: {str(e)}")
                        continue
                
                if not self.apps:
                    LOG_WARN("No valid applications found in registry")
                    self._create_default_registry()
                else:
                    LOG_INFO(f"Successfully loaded {len(self.apps)} applications")
                    
        except json.JSONDecodeError:
            LOG_ERROR("Invalid JSON format in apps registry")
            self._create_default_registry()
        except Exception as e:
            LOG_FATAL(f"Failed to load apps: {str(e)}")
            self._create_default_registry()
    
    def _create_default_registry(self) -> None:  
        self.install_default_apps()
    
    def _save_apps(self) -> None:
        apps_data = [app.manifest.to_dict() for app in self.apps]
        with open(self.apps_data_file, "w", encoding="utf-8") as f:
            json.dump(apps_data, f, indent=4)
    
    def register_app(self, app: App) -> None:
        if not isinstance(app, App):
            raise TypeError("Expected App instance")
            
        if any(a.manifest.app_id == app.manifest.app_id for a in self.apps):
            raise ValueError(f"App with ID {app.manifest.app_id} already exists")
            
        self.apps.append(app)
        self._save_apps()
        LOG_INFO(f"Registered new app: {app.manifest.name}")
    
    def remove_app(self, app_id: str) -> None:
        for i, app in enumerate(self.apps):
            if app.manifest.app_id == app_id:
                removed = self.apps.pop(i)
                self._save_apps()
                LOG_INFO(f"Removed app: {removed.manifest.name}")
                return
        raise ValueError(f"App with ID {app_id} not found")
    
    def get_app(self, app_id: str) -> App:
        for app in self.apps:
            if app.manifest.app_id == app_id:
                return app
        raise ValueError(f"App with ID {app_id} not found")
    
    def install_default_apps(self) -> None:
        default_apps = [
            AppManifest(
                app_id=SYSTEM_APP_ID,
                name="System",
                package="core.system",
                main_class="LSystem013",
                version=AppVersion(1, 0, 0),
                description="Core system components"
            ),
            AppManifest(
                app_id=FILE_EXPLORER_APP_ID,
                name="File Explorer",
                package="apps.explorer",
                main_class="FileExplorer",
                version=AppVersion(1, 0, 0),
                description="Basic file manager"
            )
        ]
        
        self.apps.extend([App(manifest) for manifest in default_apps])
        self._save_apps()
        LOG_INFO("Installed default applications")