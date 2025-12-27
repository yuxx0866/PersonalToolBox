"""
Loader Factory and Registry.

Provides a factory pattern for creating data loaders based on configuration.
Supports automatic registration and discovery of available loaders.
"""

from typing import Any, Dict, Optional, Type, List
from pathlib import Path
import pandas as pd

from .base.loader import BaseLoader


class LoaderRegistry:
    """
    Registry for managing and discovering available data loaders.
    
    Maintains a mapping of loader type names to loader classes.
    Supports automatic registration of available loaders.
    """
    
    def __init__(self):
        """Initialize an empty registry."""
        self._loaders: Dict[str, Type[BaseLoader]] = {}
    
    def register(
        self,
        loader_type: str,
        loader_class: Type[BaseLoader]
    ) -> None:
        """
        Register a loader class with a type name.
        
        Args:
            loader_type: String identifier for the loader (e.g., 'local', 'github')
            loader_class: Class that extends BaseLoader
        
        Raises:
            ValueError: If loader_type is already registered
        """
        if loader_type in self._loaders:
            raise ValueError(
                f"Loader type '{loader_type}' is already registered. "
                f"Registered types: {list(self._loaders.keys())}"
            )
        
        if not issubclass(loader_class, BaseLoader):
            raise TypeError(
                f"Loader class must extend BaseLoader, got {loader_class}"
            )
        
        self._loaders[loader_type] = loader_class
    
    def get_loader_class(self, loader_type: str) -> Type[BaseLoader]:
        """
        Get the loader class for a given type.
        
        Args:
            loader_type: String identifier for the loader
        
        Returns:
            Loader class
        
        Raises:
            ValueError: If loader_type is not registered
        """
        if loader_type not in self._loaders:
            available = list(self._loaders.keys())
            raise ValueError(
                f"Loader type '{loader_type}' is not registered. "
                f"Available types: {available}"
            )
        
        return self._loaders[loader_type]
    
    def list_available_types(self) -> List[str]:
        """
        List all registered loader types.
        
        Returns:
            List of registered loader type names
        """
        return list(self._loaders.keys())
    
    def is_registered(self, loader_type: str) -> bool:
        """
        Check if a loader type is registered.
        
        Args:
            loader_type: String identifier for the loader
        
        Returns:
            True if registered, False otherwise
        """
        return loader_type in self._loaders


class LoaderFactory:
    """
    Factory for creating data loader instances based on configuration.
    
    Uses a registry to map loader types to classes and instantiates
    the appropriate loader with merged configuration.
    """
    
    def __init__(self, registry: Optional[LoaderRegistry] = None):
        """
        Initialize the factory.
        
        Args:
            registry: Optional LoaderRegistry instance. If None, uses default registry.
        """
        self.registry = registry or _default_registry
    
    def create_loader(
        self,
        loader_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> BaseLoader:
        """
        Create a loader instance of the specified type.
        
        Args:
            loader_type: String identifier for the loader (e.g., 'local', 'github')
            config: Optional configuration dictionary to pass to the loader
        
        Returns:
            Loader instance
        
        Raises:
            ValueError: If loader_type is not registered
        """
        loader_class = self.registry.get_loader_class(loader_type)
        return loader_class(config=config)
    
    def create_loader_from_config(
        self,
        data_config: Dict[str, Any],
        config_file_path: Optional[Path] = None
    ) -> BaseLoader:
        """
        Create a loader instance from a data configuration dictionary.
        
        Args:
            data_config: Configuration dictionary with 'loader' section
                        Expected structure:
                        {
                            'loader': {
                                'type': 'local',
                                'config': {
                                    'base_directory': '...',  # Optional
                                    ...
                                }
                            }
                        }
            config_file_path: Optional path to config file (for resolving base_directory)
        
        Returns:
            Loader instance
        
        Raises:
            ValueError: If configuration is invalid or loader type not found
        """
        if 'loader' not in data_config:
            raise ValueError(
                "Configuration must contain a 'loader' section with 'type' field"
            )
        
        loader_section = data_config['loader']
        
        if 'type' not in loader_section:
            raise ValueError(
                "Loader configuration must contain a 'type' field"
            )
        
        loader_type = loader_section['type']
        loader_config = loader_section.get('config', {}).copy()
        
        # Add config_file_path to loader config if provided
        # This is used for resolving base_directory relative to config file
        if config_file_path is not None:
            loader_config['config_file_path'] = str(config_file_path)
        
        # If base_directory is not specified, it will default to config file's directory
        # (handled in file_finder._resolve_base_directory)
        
        return self.create_loader(loader_type, config=loader_config)


# Default registry instance
_default_registry = LoaderRegistry()


def _register_default_loaders() -> None:
    """Register all available loaders in the default registry."""
    # Import loaders here to avoid circular imports
    try:
        from .sources.local import LocalFileLoader
        _default_registry.register('local', LocalFileLoader)
    except ImportError:
        # LocalFileLoader not available
        pass
    
    # Future loaders will be registered here:
    # try:
    #     from .sources.github import GitHubLoader
    #     _default_registry.register('github', GitHubLoader)
    # except ImportError:
    #     pass


# Auto-register default loaders on import
_register_default_loaders()


def get_default_factory() -> LoaderFactory:
    """
    Get the default factory instance with pre-registered loaders.
    
    Returns:
        LoaderFactory instance
    """
    return LoaderFactory()


def get_loader(
    config_path: Optional[str] = None,
    loader_type: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None
) -> BaseLoader:
    """
    Convenience function to get a configured loader.
    
    This function provides a simple API to get a loader instance.
    It supports multiple ways of configuration:
    
    1. From config file (config_path specified)
    2. By type with custom config (loader_type and config specified)
    3. From default config file (no arguments)
    
    Args:
        config_path: Optional explicit path to data_config.yaml file.
                     If None, uses fallback strategy to find config file.
                     See load_data_config() for search locations.
        loader_type: Optional explicit loader type (e.g., 'local').
                    If specified, config_path is ignored.
        config: Optional configuration dictionary.
               Only used if loader_type is specified.
    
    Returns:
        Configured loader instance
    
    Raises:
        ValueError: If configuration is invalid or loader type not found
        FileNotFoundError: If config_path is specified but file doesn't exist
    
    Example:
        >>> # Load from default config file
        >>> loader = get_loader()
        
        >>> # Load from custom config file
        >>> loader = get_loader(config_path='custom/path.yaml')
        
        >>> # Load by type with custom config
        >>> loader = get_loader(loader_type='local', config={'format_handler_config_path': '...'})
    """
    from .utils.config_loader import load_data_config, get_data_config_path
    
    # If explicit loader_type is provided, use it directly
    if loader_type is not None:
        factory = get_default_factory()
        return factory.create_loader(loader_type, config=config)
    
    # Otherwise, load from config file
    config_file_path = get_data_config_path(config_path=config_path)
    data_config = load_data_config(config_path=config_path)
    factory = get_default_factory()
    return factory.create_loader_from_config(data_config, config_file_path=config_file_path)


def load_data(
    source_name: Optional[str] = None,
    source_path: Optional[str] = None,
    config_path: Optional[str] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Load data from a configured source.
    
    This is a convenience function that combines loader creation and data loading.
    It supports loading from:
    
    1. Named source in config file (source_name specified)
    2. Direct file path (source_path specified)
    3. Default source from config (no arguments, uses first source)
    
    Args:
        source_name: Optional name of source from config file (e.g., 'parquet_data')
        source_path: Optional direct file path (overrides source_name if both provided)
        config_path: Optional explicit path to data_config.yaml file.
                    If None, uses fallback strategy to find config file.
                    See load_data_config() for search locations.
        **kwargs: Additional parameters passed to loader.get_data()
                 (e.g., format, validate_before_load, etc.)
    
    Returns:
        pandas DataFrame containing the loaded data
    
    Raises:
        ValueError: If configuration is invalid, source not found, or both
                   source_name and source_path are None
        FileNotFoundError: If config_path is specified but file doesn't exist
    
    Example:
        >>> # Load named source from config
        >>> data = load_data('parquet_data')
        
        >>> # Load direct file path
        >>> data = load_data(source_path='TestData/test.csv')
        
        >>> # Load with custom config
        >>> data = load_data('csv_data', config_path='custom/path.yaml')
        
        >>> # Load with format override
        >>> data = load_data('txt_data', format='custom_txt')
    """
    from .utils.config_loader import load_data_config
    
    # Get loader from config
    loader = get_loader(config_path=config_path)
    
    # Get config file path for base_directory resolution
    from .utils.config_loader import get_data_config_path
    config_file_path = get_data_config_path(config_path=config_path)
    
    # Determine source path
    if source_path is not None:
        # Direct path provided
        file_path = source_path
        # Extract format and other params from kwargs
        format_param = kwargs.pop('format', None)
        match_strategy = kwargs.pop('match_strategy', 'first')
    elif source_name is not None:
        # Named source from config
        data_config = load_data_config(config_path=config_path)
        
        if 'sources' not in data_config:
            raise ValueError(
                "Configuration file does not contain a 'sources' section"
            )
        
        sources = data_config['sources']
        
        if source_name not in sources:
            available = list(sources.keys())
            raise ValueError(
                f"Source '{source_name}' not found in configuration. "
                f"Available sources: {available}"
            )
        
        source_config = sources[source_name]
        
        # Support both 'path' and 'pattern' fields
        if 'path' not in source_config and 'pattern' not in source_config:
            raise ValueError(
                f"Source '{source_name}' configuration must contain either a 'path' or 'pattern' field"
            )
        
        # Use pattern if available, otherwise use path
        file_path = source_config.get('pattern') or source_config.get('path')
        
        # Extract format and other params from source config
        format_param = source_config.get('format')
        match_strategy = source_config.get('match_strategy', 'first')
        
        # Merge source-specific params with kwargs (kwargs take precedence)
        source_params = {k: v for k, v in source_config.items() 
                        if k not in ['path', 'pattern', 'format', 'match_strategy', 'directory']}
        # Remove format and match_strategy from kwargs if they were passed
        kwargs.pop('format', None)
        kwargs.pop('match_strategy', None)
        
        # Add match_strategy to kwargs if specified in config
        if match_strategy:
            kwargs['match_strategy'] = match_strategy
        # Merge: source params first, then kwargs override
        merged_params = {**source_params, **kwargs}
        kwargs = merged_params
    else:
        # No source specified - try to use first source from config
        data_config = load_data_config(config_path=config_path)
        
        if 'sources' not in data_config or not data_config['sources']:
            raise ValueError(
                "No source specified and no sources found in configuration. "
                "Please specify source_name or source_path, or add sources to config."
            )
        
        # Use first source
        first_source_name = list(data_config['sources'].keys())[0]
        source_config = data_config['sources'][first_source_name]
        
        # Support both 'path' and 'pattern' fields
        if 'path' not in source_config and 'pattern' not in source_config:
            raise ValueError(
                f"Source '{first_source_name}' configuration must contain either a 'path' or 'pattern' field"
            )
        
        file_path = source_config.get('pattern') or source_config.get('path')
        format_param = source_config.get('format')
        match_strategy = source_config.get('match_strategy', 'first')
        
        # Merge source-specific params
        source_params = {k: v for k, v in source_config.items() 
                        if k not in ['path', 'pattern', 'format', 'match_strategy', 'directory']}
        
        # Add match_strategy to kwargs if specified in config
        if match_strategy:
            kwargs['match_strategy'] = match_strategy
        kwargs = {**source_params, **kwargs}
    
    # Get defaults from config
    data_config = load_data_config(config_path=config_path)
    defaults = data_config.get('defaults', {})
    validate_before_load = kwargs.pop('validate_before_load', 
                                     defaults.get('validate_before_load', True))
    
    # Load data
    return loader.get_data(
        file_path,
        validate_before_load=validate_before_load,
        format=format_param,
        **kwargs
    )


def load_all_sources(
    config_path: Optional[str] = None,
    **kwargs
) -> Dict[str, pd.DataFrame]:
    """
    Load all sources defined in the configuration file.
    
    Args:
        config_path: Optional explicit path to data_config.yaml file.
                    If None, uses fallback strategy to find config file.
                    See load_data_config() for search locations.
        **kwargs: Additional parameters passed to all loaders
                 (e.g., validate_before_load)
    
    Returns:
        Dictionary mapping source names to DataFrames
    
    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If config_path is specified but file doesn't exist
    
    Example:
        >>> # Load all sources from default config
        >>> all_data = load_all_sources()
        >>> parquet_df = all_data['parquet_data']
        >>> csv_df = all_data['csv_data']
    """
    from .utils.config_loader import load_data_config
    
    data_config = load_data_config(config_path=config_path)
    
    if 'sources' not in data_config or not data_config['sources']:
        raise ValueError(
            "No sources found in configuration file"
        )
    
    sources = data_config['sources']
    result = {}
    
    for source_name in sources:
        try:
            result[source_name] = load_data(
                source_name=source_name,
                config_path=config_path,
                **kwargs
            )
        except Exception as e:
            # Log error but continue with other sources
            # In production, you might want to use proper logging here
            print(f"Warning: Failed to load source '{source_name}': {e}")
            result[source_name] = None  # Or raise, depending on preference
    
    return result

