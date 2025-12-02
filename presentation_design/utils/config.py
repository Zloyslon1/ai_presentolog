"""
Configuration Management Module
================================

Centralized configuration management for the presentation design system.
Loads and validates configuration from JSON files with support for
environment-specific overrides.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """
    Configuration manager for the presentation design system.
    
    Loads configuration from JSON files and provides access to
    configuration parameters with validation and environment-specific overrides.
    
    Attributes:
        config_data (Dict[str, Any]): Loaded configuration dictionary
        environment (str): Current environment (development, staging, production)
    """
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "development"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to main configuration file. If None, uses default location.
            environment: Environment name for loading environment-specific overrides.
            
        Raises:
            ConfigurationError: If configuration file not found or invalid.
        """
        self.environment = environment
        self.config_data: Dict[str, Any] = {}
        
        # Determine configuration file path
        if config_path is None:
            base_dir = Path(__file__).parent.parent.parent
            config_path = base_dir / "config" / "config.json"
        
        self.config_path = Path(config_path)
        
        # Load main configuration
        self._load_config()
        
        # Load environment-specific overrides
        self._load_environment_config()
        
        # Validate configuration
        self._validate_config()
    
    def _load_config(self) -> None:
        """
        Load main configuration file.
        
        Raises:
            ConfigurationError: If file not found or JSON invalid.
        """
        if not self.config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading configuration: {e}")
    
    def _load_environment_config(self) -> None:
        """
        Load environment-specific configuration overrides.
        
        Environment config files are named config.{environment}.json
        """
        env_config_path = self.config_path.parent / f"config.{self.environment}.json"
        
        if env_config_path.exists():
            try:
                with open(env_config_path, 'r', encoding='utf-8') as f:
                    env_config = json.load(f)
                    # Merge environment config (overrides main config)
                    self._deep_merge(self.config_data, env_config)
            except Exception as e:
                # Environment config is optional, log warning but don't fail
                print(f"Warning: Could not load environment config: {e}")
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """
        Deep merge override dictionary into base dictionary.
        
        Args:
            base: Base dictionary to merge into
            override: Override dictionary with new values
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _validate_config(self) -> None:
        """
        Validate required configuration parameters.
        
        Raises:
            ConfigurationError: If required parameters are missing.
        """
        required_sections = ["authentication", "templates", "processing", "logging"]
        
        for section in required_sections:
            if section not in self.config_data:
                raise ConfigurationError(f"Required configuration section missing: {section}")
        
        # Validate authentication section
        auth_params = ["scopes", "token_path"]
        for param in auth_params:
            if param not in self.config_data["authentication"]:
                raise ConfigurationError(f"Required authentication parameter missing: {param}")
        
        # Validate templates section
        template_params = ["template_directory", "default_template"]
        for param in template_params:
            if param not in self.config_data["templates"]:
                raise ConfigurationError(f"Required template parameter missing: {param}")
        
        # Validate paths exist
        self._validate_paths()
    
    def _validate_paths(self) -> None:
        """
        Validate that required paths exist or can be created.
        
        Raises:
            ConfigurationError: If paths are invalid.
        """
        base_dir = Path(__file__).parent.parent.parent
        
        # Validate template directory
        template_dir = base_dir / self.config_data["templates"]["template_directory"]
        if not template_dir.exists():
            raise ConfigurationError(f"Template directory not found: {template_dir}")
        
        # Ensure log directory exists
        log_path = base_dir / self.config_data["logging"].get("log_file_path", "logs")
        log_dir = log_path if log_path.is_dir() else log_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure credentials directory exists
        token_path = base_dir / self.config_data["authentication"]["token_path"]
        token_dir = token_path.parent
        token_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., "authentication.scopes")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
            
        Examples:
            >>> config = Config()
            >>> config.get("authentication.scopes")
            ['https://www.googleapis.com/auth/presentations']
            >>> config.get("missing.key", "default_value")
            'default_value'
        """
        keys = key_path.split('.')
        value = self.config_data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name (e.g., "authentication")
            
        Returns:
            Configuration section dictionary
            
        Raises:
            ConfigurationError: If section not found
        """
        if section not in self.config_data:
            raise ConfigurationError(f"Configuration section not found: {section}")
        
        return self.config_data[section]
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """
        Convert relative path from config to absolute path.
        
        Args:
            relative_path: Relative path from configuration
            
        Returns:
            Absolute Path object
        """
        base_dir = Path(__file__).parent.parent.parent
        return base_dir / relative_path
    
    def reload(self) -> None:
        """
        Reload configuration from files.
        
        Useful for picking up configuration changes without restarting.
        """
        self.config_data = {}
        self._load_config()
        self._load_environment_config()
        self._validate_config()
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(environment='{self.environment}', sections={list(self.config_data.keys())})"


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None, environment: Optional[str] = None) -> Config:
    """
    Get or create global configuration instance.
    
    Args:
        config_path: Path to configuration file (only used on first call)
        environment: Environment name (only used on first call, or from env variable)
        
    Returns:
        Global Config instance
    """
    global _config_instance
    
    if _config_instance is None:
        if environment is None:
            environment = os.getenv('PRESENTATION_ENV', 'development')
        _config_instance = Config(config_path, environment)
    
    return _config_instance


def reload_config() -> None:
    """
    Reload global configuration instance.
    
    Forces re-reading of configuration files.
    """
    global _config_instance
    if _config_instance is not None:
        _config_instance.reload()
