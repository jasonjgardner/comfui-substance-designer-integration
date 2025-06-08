"""
Configuration settings for ComfyUI Substance Designer Integration Plugin.

This module provides default configuration values and settings management
for the Substance Designer integration plugin.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Default configuration values
DEFAULT_CONFIG = {
    # Tool paths (auto-detected if not specified)
    "tool_paths": {
        "sbscooker": None,
        "sbsrender": None,
        "sbsmutator": None,
        "sbsbaker": None,
        "sbsmtools": None,
        "sbsupdater": None
    },
    
    # Default processing settings
    "defaults": {
        "cooking": {
            "optimization_level": 1,
            "enable_icons": True,
            "merge_graphs": False,
            "timeout": 300  # 5 minutes
        },
        "rendering": {
            "output_format": "png",
            "bit_depth": "8",
            "cpu_count": None,  # Auto-detect
            "memory_budget": 2000,  # MB
            "timeout": 600  # 10 minutes
        },
        "batch_processing": {
            "max_workers": 2,
            "organize_by_material": True,
            "continue_on_error": True
        }
    },
    
    # Cache settings
    "cache": {
        "enabled": True,
        "max_size_mb": 1024,  # 1GB
        "cleanup_interval": 3600,  # 1 hour
        "cache_directory": None  # Auto-determined
    },
    
    # Logging settings
    "logging": {
        "level": "INFO",
        "log_to_file": False,
        "log_file": None,
        "max_log_size_mb": 10,
        "backup_count": 3
    },
    
    # Security settings
    "security": {
        "allow_absolute_paths": True,
        "restrict_to_directories": [],
        "max_file_size_mb": 100,
        "allowed_extensions": [".sbs", ".sbsar"]
    }
}

class PluginConfig:
    """Configuration manager for the Substance Designer integration plugin."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Optional path to custom configuration file
        """
        self.config_file = config_file or self._get_default_config_path()
        self.config = DEFAULT_CONFIG.copy()
        self._load_config()
        self._setup_logging()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Try to use ComfyUI's config directory if available
        comfy_config_dir = os.environ.get('COMFYUI_CONFIG_DIR')
        if comfy_config_dir:
            config_dir = os.path.join(comfy_config_dir, 'substance_designer')
        else:
            # Fall back to user's home directory
            config_dir = os.path.join(os.path.expanduser('~'), '.comfyui', 'substance_designer')
        
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, 'config.json')
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                
                # Merge user config with defaults
                self._merge_config(self.config, user_config)
                
            except Exception as e:
                logging.warning(f"Failed to load config from {self.config_file}: {e}")
    
    def _merge_config(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Recursively merge configuration dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _setup_logging(self) -> None:
        """Setup logging based on configuration."""
        log_config = self.config.get('logging', {})
        
        # Configure logging level
        level = getattr(logging, log_config.get('level', 'INFO').upper())
        logging.getLogger('substance_designer').setLevel(level)
        
        # Configure file logging if enabled
        if log_config.get('log_to_file', False):
            log_file = log_config.get('log_file')
            if not log_file:
                log_dir = os.path.dirname(self.config_file)
                log_file = os.path.join(log_dir, 'substance_designer.log')
            
            # Setup rotating file handler
            from logging.handlers import RotatingFileHandler
            handler = RotatingFileHandler(
                log_file,
                maxBytes=log_config.get('max_log_size_mb', 10) * 1024 * 1024,
                backupCount=log_config.get('backup_count', 3)
            )
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            
            logging.getLogger('substance_designer').addHandler(handler)
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save config to {self.config_file}: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration value
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the configuration value
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent dictionary
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the final value
        config[keys[-1]] = value
    
    def get_tool_path(self, tool_name: str) -> Optional[str]:
        """
        Get the path for a specific Substance tool.
        
        Args:
            tool_name: Name of the tool (e.g., 'sbscooker', 'sbsrender')
            
        Returns:
            Path to the tool or None if not configured
        """
        return self.get(f'tool_paths.{tool_name}')
    
    def set_tool_path(self, tool_name: str, path: str) -> None:
        """
        Set the path for a specific Substance tool.
        
        Args:
            tool_name: Name of the tool
            path: Path to the tool executable
        """
        self.set(f'tool_paths.{tool_name}', path)
    
    def get_cache_directory(self) -> str:
        """Get the cache directory path."""
        cache_dir = self.get('cache.cache_directory')
        if not cache_dir:
            # Use default cache directory
            config_dir = os.path.dirname(self.config_file)
            cache_dir = os.path.join(config_dir, 'cache')
        
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir

# Global configuration instance
_config_instance = None

def get_config() -> PluginConfig:
    """Get the global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = PluginConfig()
    return _config_instance

def reload_config() -> PluginConfig:
    """Reload the configuration from file."""
    global _config_instance
    _config_instance = PluginConfig()
    return _config_instance

