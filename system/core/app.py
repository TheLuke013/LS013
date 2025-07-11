import json
import uuid
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import os

from .log import *

@dataclass
class AppVersion:
    major: int
    minor: int
    patch: int

    def __post_init__(self):
        if not all(isinstance(v, int) for v in (self.major, self.minor, self.patch)):
            raise TypeError("Version components must be integers")
        if any(v < 0 for v in (self.major, self.minor, self.patch)):
            raise ValueError("Version components cannot be negative")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

@dataclass
class AppManifest:
    name: str
    package: str
    main_class: str
    version: AppVersion
    description: str = ""
    app_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dependencies: List[str] = field(default_factory=list)
    author: Optional[str] = None
    license: Optional[str] = None

    def __post_init__(self):
        if not re.match(r"^[a-z_][a-z0-9_]*(\.[a-z_][a-z0-9_]*)*$", self.package):
            raise ValueError("Invalid package name format")
        
        if not self.main_class.isidentifier():
            raise ValueError("Main class must be a valid Python identifier")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.app_id,
            "name": self.name,
            "description": self.description,
            "version": {
                "major": self.version.major,
                "minor": self.version.minor,
                "patch": self.version.patch
            },
            "package": self.package,
            "main_class": self.main_class,
            "dependencies": self.dependencies,
            "author": self.author,
            "license": self.license
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppManifest":
        version = AppVersion(
            major=data["version"]["major"],
            minor=data["version"]["minor"],
            patch=data["version"]["patch"]
        )
        
        return cls(
            name=data["name"],
            package=data["package"],
            main_class=data["main_class"],
            version=version,
            description=data.get("description", ""),
            app_id=data.get("id", str(uuid.uuid4())),
            dependencies=data.get("dependencies", []),
            author=data.get("author"),
            license=data.get("license")
        )

class App:
    def __init__(self, manifest: AppManifest, icon_path: Optional[str] = None):
        if not isinstance(manifest, AppManifest):
            raise TypeError("manifest must be an AppManifest instance")
        
        self.manifest = manifest
        self._stored_icon_path = icon_path
        self._resolved_icon_path = None
        
        self.app_id = manifest.app_id
        self.name = manifest.name
        self.package = manifest.package
        self.main_class = manifest.main_class
        self.version = str(manifest.version)
        
        if icon_path and not os.path.exists(icon_path):
            LOG_WARN(f"Icon path does not exist: {icon_path}")
            self._icon_path = None
        
    @property
    def icon_path(self) -> Optional[str]:
        if self._resolved_icon_path is None and self._stored_icon_path:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            resolved_path = os.path.abspath(os.path.join(base_dir, self._stored_icon_path))
            
            if os.path.exists(resolved_path):
                self._resolved_icon_path = resolved_path
            else:
                LOG_WARN(f"Icon path does not exist: {resolved_path}")
        
        return self._resolved_icon_path
    
    def has_icon(self) -> bool:
        return self.icon_path is not None and os.path.exists(self.icon_path)
    
    def to_dict(self) -> Dict[str, Any]:
        data = self.manifest.to_dict()
        data["icon_path"] = self._stored_icon_path
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "App":
        manifest = AppManifest.from_dict(data)
        icon_path = data.get("icon_path")
        return cls(manifest, icon_path=icon_path)