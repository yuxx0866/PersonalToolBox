"""
Configuration loader utility.

Handles loading and managing configuration from YAML files with fallback hierarchy:
1. User-provided config (highest priority)
2. Environment variables
3. Default config in module (lowest priority)
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


def _load_default_config() -> Dict[str, Any]:
    """
    Load default configuration from inside the module.
    
    Returns:
        Dictionary containing default configuration
    """
    # Get path to default config.yaml in module
    module_dir = Path(__file__).parent.parent
    config_path = module_dir / 'config.yaml'
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _load_user_config(config_path: str) -> Dict[str, Any]:
    """
    Load user-provided configuration file.
    
    Args:
        config_path: Path to user's config file
    
    Returns:
        Dictionary containing user configuration
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    config_path_obj = Path(config_path)
    
    if not config_path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path_obj, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _merge_configs(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge user configuration into default configuration.
    
    User config values override default values. Nested dictionaries are merged recursively.
    
    Args:
        default: Default configuration dictionary
        user: User configuration dictionary
    
    Returns:
        Merged configuration dictionary
    """
    result = default.copy()
    
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = _merge_configs(result[key], value)
        else:
            # Override with user value
            result[key] = value
    
    return result


def _apply_environment_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply environment variable overrides to configuration.
    
    Environment variables follow the pattern:
    FORMAT_HANDLER_<SECTION>_<KEY>=value
    
    Example:
    FORMAT_HANDLER_CSV_SEPARATOR=';'
    FORMAT_HANDLER_CUSTOM_TXT_COLUMN_SEPARATOR='|'
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Configuration dictionary with environment overrides applied
    """
    result = config.copy()
    prefix = 'FORMAT_HANDLER_'
    
    for env_key, env_value in os.environ.items():
        if not env_key.startswith(prefix):
            continue
        
        # Remove prefix and split
        key_parts = env_key[len(prefix):].lower().split('_')
        
        # Navigate/create nested structure
        current = result
        for part in key_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value (convert string to appropriate type if needed)
        final_key = key_parts[-1]
        current[final_key] = _convert_env_value(env_value)
    
    return result


def _convert_env_value(value: str) -> Any:
    """
    Convert environment variable string to appropriate type.
    
    Args:
        value: Environment variable value as string
    
    Returns:
        Converted value (str, int, float, bool, or None)
    """
    # Handle None/null
    if value.lower() in ('null', 'none', ''):
        return None
    
    # Handle booleans
    if value.lower() in ('true', 'yes', '1'):
        return True
    if value.lower() in ('false', 'no', '0'):
        return False
    
    # Handle numbers
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    
    # Return as string
    return value


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration with fallback hierarchy.
    
    Priority order (highest to lowest):
    1. Environment variables
    2. User-provided config file
    3. Default config in module
    
    Args:
        config_path: Optional path to user's config file.
                    If None, only default config and environment variables are used.
    
    Returns:
        Dictionary containing merged configuration
    
    Example:
        >>> # Use default config
        >>> config = load_config()
        
        >>> # Use custom config
        >>> config = load_config('/path/to/my_config.yaml')
    """
    # Start with default config
    config = _load_default_config()
    
    # Merge user config if provided
    if config_path:
        try:
            user_config = _load_user_config(config_path)
            config = _merge_configs(config, user_config)
        except FileNotFoundError:
            # If user config doesn't exist, continue with defaults
            pass
    
    # Apply environment variable overrides
    config = _apply_environment_overrides(config)
    
    return config


def get_format_config(
    format_name: str,
    config_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get configuration for a specific format.
    
    Args:
        format_name: Name of the format (e.g., 'csv', 'custom_txt')
        config_path: Optional path to user's config file
    
    Returns:
        Dictionary containing format-specific configuration
    
    Example:
        >>> csv_config = get_format_config('csv')
        >>> # Returns: {'separator': ',', 'encoding': 'utf-8'}
    """
    full_config = load_config(config_path)
    
    # Get format config from formats section
    formats_config = full_config.get('formats', {})
    format_config = formats_config.get(format_name, {})
    
    # Merge with defaults
    defaults = full_config.get('defaults', {})
    
    # Format-specific config overrides defaults
    result = defaults.copy()
    result.update(format_config)
    
    return result

