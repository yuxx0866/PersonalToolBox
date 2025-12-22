"""
Data Loader Module

A scalable Python module for importing data from various sources.
Currently supports:
- Local files (CSV, Custom TXT, Parquet via format_handler module)

Designed for easy extension to support additional sources in the future:
- GitHub
- SharePoint
- Azure (Blob Storage, Data Lake, etc.)
- And more...

Usage (Configuration-driven - Recommended):
    from data_loader import load_data, get_loader
    
    # Load named source from config/data_config.yaml
    data = load_data('parquet_data')
    
    # Load all sources
    all_data = load_all_sources()
    
    # Get configured loader
    loader = get_loader()
    data = loader.get_data('path/to/file.csv')

Usage (Direct - Backward compatible):
    from data_loader.sources.local import LocalFileLoader
    
    loader = LocalFileLoader()
    data = loader.get_data('path/to/file.csv')
    
    # With format override
    data = loader.get_data('path/to/file.txt', format='custom_txt')
"""

__version__ = '0.1.0'

# Export main API functions
from .factory import (
    get_loader,
    load_data,
    load_all_sources,
    LoaderFactory,
    LoaderRegistry,
    get_default_factory
)

# Export base classes and loaders for direct use
from .base.loader import BaseLoader
from .sources.local import LocalFileLoader

__all__ = [
    # Main API
    'get_loader',
    'load_data',
    'load_all_sources',
    'LoaderFactory',
    'LoaderRegistry',
    'get_default_factory',
    # Base classes
    'BaseLoader',
    # Loaders
    'LocalFileLoader',
]

