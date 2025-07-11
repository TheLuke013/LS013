import os
import json
from typing import List

from core.app import App, AppManifest, AppVersion
from core.constants import *
from .log import *

class AppsManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'apps'):
            self.apps = []
            self.active_apps = []
            self.apps_data_file = APPS_DATA_FILENAME
            self._load_apps()
        
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
                        icon_path = app_data.get("icon_path")
                        app = App(manifest, icon_path=icon_path)
                        self.apps.append(app)
                        LOG_INFO(f"Loaded app: {app.name}, icon: {app.icon_path}")
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
            LOG_CRITICAL(f"Failed to load apps: {str(e)}")
            self._create_default_registry()
    
    def _create_default_registry(self) -> None:  
        self.install_default_apps()
    
    def _save_apps(self) -> None:
        apps_data = []
        for app in self.apps:
            app_data = app.to_dict()
            apps_data.append(app_data)
        
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
        default_apps_data = [
            {
                "manifest": AppManifest(
                    app_id=SYSTEM_APP_ID,
                    name="System",
                    package="core.system",
                    main_class="LSystem013",
                    version=AppVersion(1, 0, 0),
                    description="Core system components"
                ),
                "icon": SYSTEM_ICON
            },
            {
                "manifest": AppManifest(
                    app_id=FILE_EXPLORER_APP_ID,
                    name="File Explorer",
                    package="apps.explorer",
                    main_class="FileExplorer",
                    version=AppVersion(1, 0, 0),
                    description="Basic file manager"
                ),
                "icon": EXPLORER_ICON
            }
        ]
        
        for app_data in default_apps_data:
            if not any(app.app_id == app_data["manifest"].app_id for app in self.apps):
                try:
                    new_app = App(
                        manifest=app_data["manifest"],
                        icon_path=app_data["icon"]
                    )
                    self.apps.append(new_app)
                    LOG_INFO(f"Added default app: {app_data['manifest'].name}")
                except Exception as e:
                    LOG_ERROR(f"Failed to add default app {app_data['manifest'].name}: {str(e)}")
        
        if len(default_apps_data) > 0:
            self._save_apps()
            LOG_INFO(f"Installed {len(default_apps_data)} default applications")