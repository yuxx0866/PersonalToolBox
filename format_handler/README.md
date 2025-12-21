# Format Handler Module

A reusable Python module for parsing and handling various file formats.

## Overview

This module provides a unified interface for parsing different file formats into pandas DataFrames. It's designed to be used by data loaders and other data processing tools.

**Currently Supported:**
- **CSV**: Comma-separated values files
- **Custom TXT**: Text files with configurable column and row separators
- **Parquet**: Columnar storage format (requires pyarrow or fastparquet)

**Designed for Future Extension:**
- **Excel**: xlsx, xls files
- **JSON**: JSON files with various structures
- **And more**: Easy to add new formats

## Project Structure

```
format_handler/
├── __init__.py              # Main module entry point
├── README.md                # This file
├── config.yaml              # Configuration file
├── pyproject.toml           # Project configuration
├── base/                    # Base classes and interfaces
│   ├── __init__.py
│   └── handler.py          # FileFormatHandler base class
├── handlers/                # Format handler implementations
│   ├── __init__.py
│   ├── csv_handler.py      # CSV format handler
│   └── custom_txt_handler.py # Custom TXT format handler
├── registry.py              # Format registry for handler management
└── tests/                   # Test suite
    ├── __init__.py
    ├── test_csv_handler.py
    ├── test_custom_txt_handler.py
    └── test_registry.py
```

## Design Principles

1. **Modularity**: Each format has its own handler
2. **Extensibility**: Easy to add new formats by creating new handlers
3. **Configurability**: Format-specific settings via configuration
4. **Reusability**: Can be used by any data loading module
5. **Type Safety**: Always returns pandas DataFrame

## Usage

### Basic Usage

```python
from format_handler import get_handler

# Auto-detect format by file extension
handler = get_handler('data.csv')
df = handler.load('data.csv')

# Explicit format override
handler = get_handler('data.txt', format_override='custom_txt')
df = handler.load('data.txt')
```

### Advanced Usage

```python
from format_handler import FormatRegistry, CSVFormatHandler, CustomTXTFormatHandler

# Create custom registry
registry = FormatRegistry()

# Register handlers with custom config
csv_handler = CSVFormatHandler(config={'separator': ';', 'encoding': 'latin-1'})
registry.register(csv_handler, priority=10)

custom_txt_handler = CustomTXTFormatHandler(
    config={
        'column_separator': '|',
        'row_separator': '\n'
    }
)
registry.register(custom_txt_handler, priority=5)

# Use registry
handler = registry.get_handler('data.csv')
df = handler.load('data.csv')
```

### Custom Separators

```python
from format_handler import get_handler

# Load custom TXT with different separators
handler = get_handler('data.txt')
df = handler.load(
    'data.txt',
    column_separator='|',  # Override default '*endf*'
    row_separator='\n'     # Override default '*endr*'
)

# Load Parquet files
handler = get_handler('data.parquet')
df = handler.load('data.parquet')

# Parquet with column selection
df = handler.load('data.parquet', columns=['col1', 'col2'])
```

## Configuration

Configuration is managed through `config.yaml`. See the configuration file for available options.

Key configuration sections:
- **formats**: Format-specific settings (separators, encoding, etc.)
- **defaults**: Default settings for all formats

## Adding New Format Handlers

To add a new format handler:

1. Create a new file in `handlers/` (e.g., `handlers/excel_handler.py`)
2. Extend the `FileFormatHandler` class from `base/handler.py`:
   ```python
   from ..base.handler import FileFormatHandler
   
   class ExcelFormatHandler(FileFormatHandler):
       def can_handle(self, source, format_hint=None):
           # Your implementation
           pass
       
       def load(self, source, **kwargs):
           # Your implementation
           pass
       
       def get_supported_extensions(self):
           return ['.xlsx', '.xls']
   ```
3. Register the handler in `registry.py` or register it manually
4. Add tests in `tests/test_excel_handler.py`
5. Update `config.yaml` with format-specific configuration

## Installation

```bash
pip install -e .
```

## Development

### Running Tests

```bash
pytest tests/
```

## License


## Contributing

