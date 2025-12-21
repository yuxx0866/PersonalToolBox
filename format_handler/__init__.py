"""
Format Handler Module

A reusable Python module for parsing and handling various file formats.
Designed to be used by data loaders and other data processing tools.

Currently supports:
- CSV files
- Custom TXT files (with configurable separators)

Designed for easy extension to support additional formats:
- Excel (xlsx, xls)
- JSON
- Parquet
- And more...

Usage:
    from format_handler import get_handler, FormatRegistry
    
    # Get handler for a file
    handler = get_handler('data.csv')
    df = handler.load('data.csv')
    
    # Or use registry directly
    registry = FormatRegistry()
    handler = registry.get_handler('data.txt', format_override='custom_txt')
    df = handler.load('data.txt', column_separator='*endf*', row_separator='*endr*')
"""

__version__ = '0.1.0'

# Import main components
from .registry import FormatRegistry, get_handler, get_default_registry, reset_default_registry
from .base.handler import FileFormatHandler
from .utils.config_loader import load_config, get_format_config

# Import handlers for convenience
from .handlers.csv_handler import CSVFormatHandler
from .handlers.custom_txt_handler import CustomTXTFormatHandler
from .handlers.parquet_handler import ParquetFormatHandler

__all__ = [
    'FormatRegistry',
    'get_handler',
    'get_default_registry',
    'reset_default_registry',
    'FileFormatHandler',
    'CSVFormatHandler',
    'CustomTXTFormatHandler',
    'ParquetFormatHandler',
    'load_config',
    'get_format_config',
]

