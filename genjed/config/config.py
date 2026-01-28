"""Genjed Configuration Loader.

Loads configuration from config.yaml and supports environment variable overrides.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Configuration manager for Genjed.ai workflow engine."""
    
    _instance: Optional['Config'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls) -> 'Config':
        """Singleton pattern for configuration."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Load configuration from config.yaml file."""
        config_path = Path(__file__).parent / "config.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)
        
        # Process environment variable placeholders
        self._process_env_vars(self._config)
    
    def _process_env_vars(self, config: Any, parent_key: str = "") -> Any:
        """Recursively process environment variable placeholders."""
        if isinstance(config, dict):
            for key, value in config.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                config[key] = self._process_env_vars(value, new_key)
        elif isinstance(config, list):
            for i, item in enumerate(config):
                config[i] = self._process_env_vars(item, f"{parent_key}[{i}]")
        elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
            env_var = config[2:-1]
            env_value = os.getenv(env_var)
            if env_value is None:
                return ""
            return env_value
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    @property
    def replicate(self) -> Dict[str, Any]:
        return self._config.get('replicate', {})
    
    @property
    def database(self) -> Dict[str, Any]:
        return self._config.get('database', {})
    
    @property
    def redis(self) -> Dict[str, Any]:
        return self._config.get('redis', {})
    
    @property
    def qa(self) -> Dict[str, Any]:
        return self._config.get('qa', {})
    
    @property
    def distribution(self) -> Dict[str, Any]:
        return self._config.get('distribution', {})
    
    @property
    def analytics(self) -> Dict[str, Any]:
        return self._config.get('analytics', {})
    
    @property
    def storage(self) -> Dict[str, Any]:
        return self._config.get('storage', {})
    
    @property
    def app(self) -> Dict[str, Any]:
        return self._config.get('app', {})
    
    @property
    def video(self) -> Dict[str, Any]:
        return self._config.get('video', {})
    
    @property
    def audio(self) -> Dict[str, Any]:
        return self._config.get('audio', {})
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()


def get_config() -> Config:
    """Get the singleton configuration instance."""
    return Config()
