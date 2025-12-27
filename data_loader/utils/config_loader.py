"""
Configuration loader utility.

Handles loading and managing configuration from YAML files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to config.yaml file. If None, looks for config.yaml
                     in the data_loader module directory.
    
    Returns:
        Dictionary containing merged configuration from file and environment variables
    """
    # Implementation will be added here
    # - Load YAML file
    # - Override with environment variables
    # - Return merged config
    pass


def get_config(section: Optional[str] = None) -> Any:
    """
    Get configuration value(s).
    
    Args:
        section: Optional section name to retrieve. If None, returns entire config.
    
    Returns:
        Configuration value(s)
    """
    # Implementation will be added here
    pass


def get_credentials(service: str) -> Dict[str, Any]:
    """
    Get credentials for a specific service.
    
    Args:
        service: Service name (e.g., 'github', 'sharepoint', 'azure')
    
    Returns:
        Dictionary containing credentials for the service
    """
    # Implementation will be added here
    pass


def _find_data_config_file() -> Optional[Path]:
    """
    Find data_config.yaml file using standard fallback strategy.
    
    Search order (first found wins):
    1. Environment variable DATA_LOADER_CONFIG_PATH
    2. Current working directory: ./config/data_config.yaml
    3. Current working directory: ./data_config.yaml
    4. User home directory: ~/.data_loader/data_config.yaml
    5. User config directory: ~/.config/data_loader/data_config.yaml (Linux/macOS)
    6. Application data directory: %APPDATA%/data_loader/data_config.yaml (Windows)
    
    Returns:
        Path to config file if found, None otherwise
    """
    # Priority 1: Environment variable
    env_path = os.environ.get('DATA_LOADER_CONFIG_PATH')
    if env_path:
        path = Path(env_path).expanduser().resolve()
        if path.exists():
            return path
    
    # Priority 2: Current working directory - config/data_config.yaml
    cwd_config = Path.cwd() / 'config' / 'data_config.yaml'
    if cwd_config.exists():
        return cwd_config
    
    # Priority 3: Current working directory - data_config.yaml
    cwd_direct = Path.cwd() / 'data_config.yaml'
    if cwd_direct.exists():
        return cwd_direct
    
    # Priority 4: User home directory
    home_dir = Path.home()
    home_config = home_dir / '.data_loader' / 'data_config.yaml'
    if home_config.exists():
        return home_config
    
    # Priority 5: XDG config directory (Linux/macOS) or AppData (Windows)
    if os.name == 'nt':  # Windows
        appdata = os.environ.get('APPDATA')
        if appdata:
            appdata_config = Path(appdata) / 'data_loader' / 'data_config.yaml'
            if appdata_config.exists():
                return appdata_config
    else:  # Linux/macOS
        xdg_config = os.environ.get('XDG_CONFIG_HOME')
        if xdg_config:
            xdg_config_path = Path(xdg_config) / 'data_loader' / 'data_config.yaml'
            if xdg_config_path.exists():
                return xdg_config_path
        else:
            # Fallback to ~/.config
            xdg_fallback = home_dir / '.config' / 'data_loader' / 'data_config.yaml'
            if xdg_fallback.exists():
                return xdg_fallback
    
    return None


def load_data_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load data loading configuration from data_config.yaml file.
    
    This function loads the user-facing data configuration file that specifies
    which loader to use and which data sources to load.
    
    Config file discovery uses a fallback strategy (see _find_data_config_file()):
    1. Explicit path (if provided)
    2. Environment variable DATA_LOADER_CONFIG_PATH
    3. Current working directory: ./config/data_config.yaml
    4. Current working directory: ./data_config.yaml
    5. User home: ~/.data_loader/data_config.yaml
    6. User config: ~/.config/data_loader/data_config.yaml (Linux/macOS)
    7. AppData: %APPDATA%/data_loader/data_config.yaml (Windows)
    
    Args:
        config_path: Optional explicit path to data_config.yaml file.
                   If None, uses fallback strategy to find config file.
                   If provided, must exist or FileNotFoundError is raised.
    
    Returns:
        Dictionary containing the loaded configuration
    
    Raises:
        FileNotFoundError: If config_path is provided but doesn't exist, or
                          if no config file is found in any fallback location
        yaml.YAMLError: If config file is invalid YAML
    
    Example:
        >>> # Use fallback discovery
        >>> config = load_data_config()
        
        >>> # Use explicit path
        >>> config = load_data_config('/path/to/config.yaml')
        
        >>> # Use environment variable
        >>> # Set: export DATA_LOADER_CONFIG_PATH=/path/to/config.yaml
        >>> config = load_data_config()
    """
    # If explicit path provided, use it directly
    if config_path is not None:
        config_path_obj = Path(config_path).expanduser().resolve()
        if not config_path_obj.exists():
            raise FileNotFoundError(
                f"Data configuration file not found at specified path: {config_path_obj}. "
                f"Please check the path or use fallback discovery by omitting config_path."
            )
    else:
        # Use fallback strategy to find config file
        config_path_obj = _find_data_config_file()
        if config_path_obj is None:
            # Provide helpful error message with search locations
            search_locations = [
                f"Environment variable: DATA_LOADER_CONFIG_PATH",
                f"Current directory: {Path.cwd() / 'config' / 'data_config.yaml'}",
                f"Current directory: {Path.cwd() / 'data_config.yaml'}",
                f"User home: {Path.home() / '.data_loader' / 'data_config.yaml'}",
            ]
            if os.name == 'nt':
                appdata = os.environ.get('APPDATA', '')
                if appdata:
                    search_locations.append(f"AppData: {Path(appdata) / 'data_loader' / 'data_config.yaml'}")
            else:
                search_locations.append(f"XDG config: {Path.home() / '.config' / 'data_loader' / 'data_config.yaml'}")
            
            locations_str = "\n  - ".join(search_locations)
            raise FileNotFoundError(
                f"Data configuration file 'data_config.yaml' not found in any standard location.\n\n"
                f"Searched locations:\n  - {locations_str}\n\n"
                f"Please either:\n"
                f"  1. Create data_config.yaml in one of the above locations, or\n"
                f"  2. Set DATA_LOADER_CONFIG_PATH environment variable, or\n"
                f"  3. Provide explicit path: load_data_config(config_path='path/to/config.yaml')"
            )
    
    # Load YAML file
    try:
        with open(config_path_obj, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(
            f"Error parsing YAML file {config_path_obj}: {e}"
        ) from e
    
    if config is None:
        config = {}
    
    # Apply environment variable overrides
    # Format: DATA_LOADER_<SECTION>_<KEY>=value
    # Example: DATA_LOADER_LOADER_TYPE=local
    env_prefix = 'DATA_LOADER_'
    
    for key, value in os.environ.items():
        if key.startswith(env_prefix):
            # Remove prefix and split into sections
            key_parts = key[len(env_prefix):].lower().split('_')
            
            # Navigate/create nested structure
            current = config
            for part in key_parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set value (convert string to appropriate type)
            final_key = key_parts[-1]
            current[final_key] = _convert_env_value(value)
    
    return config


def _convert_env_value(value: str) -> Any:
    """
    Convert environment variable string to appropriate Python type.
    
    Args:
        value: String value from environment variable
    
    Returns:
        Converted value (bool, int, float, or str)
    """
    # Try boolean
    if value.lower() in ('true', 'false'):
        return value.lower() == 'true'
    
    # Try integer
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string
    return value


def get_data_config_path(config_path: Optional[str] = None) -> Path:
    """
    Get the path to the data_config.yaml file.
    
    This is useful for resolving relative base_directory paths
    relative to the config file location.
    
    Args:
        config_path: Optional explicit path to data_config.yaml file.
                   If None, uses fallback strategy to find config file.
    
    Returns:
        Path to the config file
    
    Raises:
        FileNotFoundError: If config file is not found
    """
    if config_path is not None:
        config_path_obj = Path(config_path).expanduser().resolve()
        if not config_path_obj.exists():
            raise FileNotFoundError(
                f"Data configuration file not found at specified path: {config_path_obj}. "
                f"Please check the path or use fallback discovery by omitting config_path."
            )
        return config_path_obj
    else:
        config_path_obj = _find_data_config_file()
        if config_path_obj is None:
            # Provide helpful error message with search locations
            search_locations = [
                f"Environment variable: DATA_LOADER_CONFIG_PATH",
                f"Current directory: {Path.cwd() / 'config' / 'data_config.yaml'}",
                f"Current directory: {Path.cwd() / 'data_config.yaml'}",
                f"User home: {Path.home() / '.data_loader' / 'data_config.yaml'}",
            ]
            if os.name == 'nt':
                appdata = os.environ.get('APPDATA', '')
                if appdata:
                    search_locations.append(f"AppData: {Path(appdata) / 'data_loader' / 'data_config.yaml'}")
            else:
                search_locations.append(f"XDG config: {Path.home() / '.config' / 'data_loader' / 'data_config.yaml'}")
            
            locations_str = "\n  - ".join(search_locations)
            raise FileNotFoundError(
                f"Data configuration file 'data_config.yaml' not found in any standard location.\n\n"
                f"Searched locations:\n  - {locations_str}\n\n"
                f"Please either:\n"
                f"  1. Create data_config.yaml in one of the above locations, or\n"
                f"  2. Set DATA_LOADER_CONFIG_PATH environment variable, or\n"
                f"  3. Provide explicit path: get_data_config_path(config_path='path/to/config.yaml')"
            )
        return config_path_obj

