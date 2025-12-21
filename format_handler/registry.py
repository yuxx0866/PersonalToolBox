"""
Format registry for managing and routing to format handlers.

This module provides a registry pattern for managing file format handlers
and automatically selecting the appropriate handler for a given file.
"""

from typing import Dict, List, Optional, Tuple
from .base.handler import FileFormatHandler


class FormatRegistry:
    """
    Registry for managing file format handlers.
    
    Handles registration, lookup, and routing of format handlers.
    Supports priority-based handler selection and format override.
    """
    
    def __init__(self):
        """
        Initialize the format registry.
        """
        self._handlers: List[Tuple[int, FileFormatHandler]] = []
        self._extension_map: Dict[str, FileFormatHandler] = {}
        self._format_name_map: Dict[str, FileFormatHandler] = {}
    
    def register(
        self,
        handler: FileFormatHandler,
        priority: int = 0
    ) -> None:
        """
        Register a format handler.
        
        Args:
            handler: Format handler instance to register
            priority: Priority for handler selection (higher = checked first)
                     Default: 0
        
        Example:
            >>> registry = FormatRegistry()
            >>> csv_handler = CSVFormatHandler()
            >>> registry.register(csv_handler, priority=10)
        """
        # Add to handlers list (sorted by priority)
        self._handlers.append((priority, handler))
        self._handlers.sort(key=lambda x: x[0], reverse=True)
        
        # Update extension map
        for ext in handler.get_supported_extensions():
            # Only map if not already mapped (first handler wins)
            if ext not in self._extension_map:
                self._extension_map[ext.lower()] = handler
        
        # Update format name map
        format_name = handler.get_format_name()
        self._format_name_map[format_name.lower()] = handler
    
    def get_handler(
        self,
        source: str,
        format_override: Optional[str] = None
    ) -> FileFormatHandler:
        """
        Get the appropriate handler for a given source.
        
        Args:
            source: File path or identifier
            format_override: Optional explicit format name to use
                           (e.g., 'csv', 'custom_txt')
        
        Returns:
            Format handler that can process the source
        
        Raises:
            ValueError: If no handler can process the source
        
        Example:
            >>> registry = FormatRegistry()
            >>> handler = registry.get_handler('data.csv')
            >>> handler = registry.get_handler('data.txt', format_override='custom_txt')
        """
        # Priority 1: Explicit format override
        if format_override:
            format_key = format_override.lower()
            if format_key in self._format_name_map:
                return self._format_name_map[format_key]
            # Try to find handler that accepts this format hint
            for _, handler in self._handlers:
                if handler.can_handle(source, format_hint=format_override):
                    return handler
        
        # Priority 2: File extension mapping
        if isinstance(source, str):
            # Extract extension
            if '.' in source:
                ext = '.' + source.rsplit('.', 1)[1].lower()
                if ext in self._extension_map:
                    return self._extension_map[ext]
        
        # Priority 3: Try all handlers (in priority order)
        for _, handler in self._handlers:
            if handler.can_handle(source):
                return handler
        
        # No handler found
        raise ValueError(
            f"No format handler found for source: {source}. "
            f"Supported formats: {self.list_supported_formats()}"
        )
    
    def list_supported_formats(self) -> List[str]:
        """
        Get list of all supported format names.
        
        Returns:
            List of format names (e.g., ['csv', 'custom_txt'])
        """
        return list(self._format_name_map.keys())
    
    def list_supported_extensions(self) -> List[str]:
        """
        Get list of all supported file extensions.
        
        Returns:
            List of file extensions (e.g., ['.csv', '.txt'])
        """
        return list(self._extension_map.keys())
    
    def clear(self) -> None:
        """
        Clear all registered handlers.
        
        Useful for testing or resetting the registry.
        """
        self._handlers.clear()
        self._extension_map.clear()
        self._format_name_map.clear()


# Global registry instance
_default_registry: Optional[FormatRegistry] = None
_default_config_path: Optional[str] = None


def reset_default_registry() -> None:
    """
    Reset the default registry.
    
    Useful when you want to reload handlers with different configuration.
    """
    global _default_registry, _default_config_path
    _default_registry = None
    _default_config_path = None


def get_default_registry(config_path: Optional[str] = None) -> FormatRegistry:
    """
    Get or create the default global registry.
    
    Args:
        config_path: Optional path to configuration file.
                    If provided and different from previous call,
                    registry will be reset and recreated.
    
    Returns:
        Default FormatRegistry instance with built-in handlers registered
    """
    global _default_registry, _default_config_path
    
    # Reset if config_path changed
    if _default_registry is not None and config_path != _default_config_path:
        reset_default_registry()
    
    if _default_registry is None:
        _default_registry = FormatRegistry()
        _default_config_path = config_path
        _register_default_handlers(_default_registry, config_path)
    
    return _default_registry


def _register_default_handlers(registry: FormatRegistry, config_path: Optional[str] = None) -> None:
    """
    Register built-in format handlers with configuration.
    
    Args:
        registry: Registry instance to register handlers with
        config_path: Optional path to configuration file
    """
    # Import handlers and config loader here to avoid circular imports
    from .handlers.csv_handler import CSVFormatHandler
    from .handlers.custom_txt_handler import CustomTXTFormatHandler
    from .handlers.parquet_handler import ParquetFormatHandler
    from .utils.config_loader import get_format_config
    
    # Load configuration for each format
    csv_config = get_format_config('csv', config_path)
    custom_txt_config = get_format_config('custom_txt', config_path)
    parquet_config = get_format_config('parquet', config_path)
    
    # Register handlers with priorities and configuration
    # Higher priority = checked first
    registry.register(CSVFormatHandler(config=csv_config), priority=10)
    registry.register(ParquetFormatHandler(config=parquet_config), priority=8)
    registry.register(CustomTXTFormatHandler(config=custom_txt_config), priority=5)


def get_handler(
    source: str,
    format_override: Optional[str] = None,
    registry: Optional[FormatRegistry] = None,
    config_path: Optional[str] = None
) -> FileFormatHandler:
    """
    Convenience function to get a handler for a source.
    
    Args:
        source: File path or identifier
        format_override: Optional explicit format name
        registry: Optional registry instance (uses default if None)
        config_path: Optional path to configuration file (only used if registry is None)
    
    Returns:
        Format handler that can process the source
    
    Example:
        >>> handler = get_handler('data.csv')
        >>> df = handler.load('data.csv')
        
        >>> # With custom config
        >>> handler = get_handler('data.csv', config_path='/path/to/config.yaml')
    """
    if registry is None:
        registry = get_default_registry(config_path)
    
    return registry.get_handler(source, format_override=format_override)

