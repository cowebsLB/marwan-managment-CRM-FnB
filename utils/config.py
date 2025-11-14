"""
Configuration Management Module for Marwan Management CRM
Handles reading/writing setup configuration and tracking setup completion
"""
import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Optional, Any


def get_base_path():
    """Get the base path for the application (works with PyInstaller)"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.dirname(__file__))


def get_config_path() -> Path:
    """Get the path to the configuration file"""
    return Path(get_base_path()) / "config.json"


def get_log_path() -> Path:
    """Get the path to the setup log file"""
    return Path(get_base_path()) / "setup.log"


def setup_logging():
    """Setup logging for configuration operations"""
    log_path = get_log_path()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()

# Current config version - increment when wizard should re-run
CONFIG_VERSION = "1.0"


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values"""
    base_path = get_base_path()
    return {
        "setup_complete": False,
        "config_version": CONFIG_VERSION,
        "installation_dir": base_path,
        "database_path": os.path.join(base_path, "restaurant_crm.db"),
        "shortcuts": {
            "desktop": True,
            "start_menu": True,
            "startup": False
        },
        "restaurant_name": "",
        "currency": "USD",
        "date_format": "MM/DD/YYYY"
    }


def get_config() -> Dict[str, Any]:
    """
    Read configuration from file
    
    Returns:
        Dictionary with configuration values, or default config if file doesn't exist
    """
    config_path = get_config_path()
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                default_config = get_default_config()
                default_config.update(config)
                return default_config
        else:
            logger.info("Config file not found, returning defaults")
            return get_default_config()
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing config file: {e}")
        return get_default_config()
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        return get_default_config()


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    config_path = get_config_path()
    
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write config file
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Configuration saved successfully to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving config file: {e}")
        return False


def set_config(key: str, value: Any) -> bool:
    """
    Set a specific configuration value
    
    Args:
        key: Configuration key (supports nested keys with dot notation, e.g., "shortcuts.desktop")
        value: Value to set
        
    Returns:
        True if successful, False otherwise
    """
    config = get_config()
    
    # Handle nested keys
    if '.' in key:
        keys = key.split('.')
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        current[keys[-1]] = value
    else:
        config[key] = value
    
    return save_config(config)


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value
    
    Args:
        key: Configuration key (supports nested keys with dot notation)
        default: Default value if key doesn't exist
        
    Returns:
        Configuration value or default
    """
    config = get_config()
    
    # Handle nested keys
    if '.' in key:
        keys = key.split('.')
        current = config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
    else:
        return config.get(key, default)


def is_setup_complete() -> bool:
    """
    Check if setup has been completed
    
    Returns:
        True if setup is complete, False otherwise
    """
    return get_config_value("setup_complete", False)


def should_rerun_wizard() -> bool:
    """
    Check if wizard should be re-run due to config version mismatch
    
    Returns:
        True if wizard should re-run, False otherwise
    """
    saved_version = get_config_value("config_version", "0.0")
    return saved_version != CONFIG_VERSION


def save_setup_config(
    installation_dir: str,
    database_path: str,
    shortcuts: Dict[str, bool],
    restaurant_name: str,
    currency: str = "USD",
    date_format: str = "MM/DD/YYYY"
) -> bool:
    """
    Save setup configuration after wizard completion
    
    Args:
        installation_dir: Installation directory path
        database_path: Database file path
        shortcuts: Dictionary with shortcut preferences
        restaurant_name: Restaurant/business name
        currency: Currency code
        date_format: Date format preference
        
    Returns:
        True if successful, False otherwise
    """
    config = get_config()
    config.update({
        "setup_complete": True,
        "config_version": CONFIG_VERSION,
        "installation_dir": installation_dir,
        "database_path": database_path,
        "shortcuts": shortcuts,
        "restaurant_name": restaurant_name,
        "currency": currency,
        "date_format": date_format
    })
    
    return save_config(config)

