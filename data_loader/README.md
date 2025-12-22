# Data Loader Module

A scalable Python module for importing data from various sources.

## Overview

This module provides a unified interface for loading data from multiple sources.

**Currently Supported:**
- **Local Files**: CSV, Custom TXT (with configurable separators), Parquet, and more
  - Uses the `format_handler` module for format parsing
  - Automatically detects file format from extension
  - Supports explicit format specification

**Designed for Future Extension:**
- **GitHub**: Raw files, releases, repositories
- **SharePoint**: Files, lists, and document libraries
- **Azure**: Blob Storage, Data Lake, SQL Database, and more
- **Extensible**: Easy to add new data sources by extending the base class

## Project Structure

```
data_loader/
├── __init__.py              # Main module entry point
├── README.md                # This file
├── config.yaml              # Configuration file
├── base/                    # Base classes and interfaces
│   ├── __init__.py
│   └── loader.py           # Abstract base class for all loaders
├── sources/                  # Data source implementations
│   ├── __init__.py
│   └── local.py            # Local file loader
│   # Future sources can be added here:
│   # ├── github.py         # GitHub loader (to be added)
│   # ├── sharepoint.py     # SharePoint loader (to be added)
│   # └── azure.py          # Azure loader (to be added)
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── config_loader.py    # Configuration management
│   ├── logger.py           # Logging utilities
│   └── validators.py       # Data validation helpers
└── tests/                   # Test suite
    ├── __init__.py
    └── test_local.py
    # Future test files can be added here:
    # ├── test_github.py     # (to be added)
    # ├── test_sharepoint.py # (to be added)
    # └── test_azure.py      # (to be added)
```

## Design Principles

1. **Modularity**: Each data source is a separate module
2. **Extensibility**: Easy to add new data sources by extending base classes
3. **Configuration**: Centralized configuration management
4. **Error Handling**: Consistent error handling across all sources
5. **Type Safety**: Type hints for better code quality
6. **Testing**: Comprehensive test coverage

## Dependencies

The `LocalFileLoader` requires the `format_handler` module to be installed and accessible.
The `format_handler` module handles parsing of different file formats (CSV, Custom TXT, Parquet, etc.).

Make sure `format_handler` is installed:
```bash
cd format_handler
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from data_loader.sources.local import LocalFileLoader

# Initialize the local file loader
loader = LocalFileLoader()

# Load CSV file (format auto-detected from extension)
data = loader.get_data('path/to/file.csv')

# Load Parquet file
data = loader.get_data('path/to/file.parquet')

# Load custom TXT file with explicit format specification
data = loader.get_data(
    'path/to/file.txt',
    format='custom_txt',
    column_separator='*endf*',
    row_separator='*endr*'
)
```

### Advanced Usage

```python
from data_loader.sources.local import LocalFileLoader
from data_loader.utils.config_loader import load_config

# Use specific loader with custom configuration
config = load_config()
config['format_handler_config_path'] = '/path/to/format_handler/config.yaml'
local_loader = LocalFileLoader(config=config)

# Load CSV with custom encoding
data = local_loader.get_data(
    source='path/to/file.csv',
    encoding='latin-1',
    sep=';'
)

# Load Parquet with specific columns
data = local_loader.get_data(
    source='path/to/file.parquet',
    columns=['col1', 'col2', 'col3'],
    engine='pyarrow'
)

# Skip validation for performance (if you're sure file exists)
data = local_loader.get_data(
    source='path/to/file.csv',
    validate_before_load=False
)
```

### Supported File Formats

The `LocalFileLoader` supports the following formats (via `format_handler`):

- **CSV**: Comma-separated values files (`.csv`)
  - Parameters: `sep`, `encoding`, `skiprows`, etc.
  
- **Custom TXT**: Text files with custom separators (`.txt`)
  - Parameters: `column_separator`, `row_separator`
  - Default: `*endf*` for columns, `*endr*` for rows
  
- **Parquet**: Columnar storage format (`.parquet`)
  - Parameters: `engine`, `columns`, `filters`, etc.
  
New formats can be added to the `format_handler` module and will automatically
be available to `LocalFileLoader`.

## Configuration

Configuration is managed through `config.yaml`. See the configuration file for available options.

Key configuration sections:
- **credentials**: API keys, tokens, connection strings
- **defaults**: Default settings for each source type
  - **local**: Local file loader settings
    - `format_handler_config_path`: Optional path to format_handler config file
- **logging**: Logging configuration
- **cache**: Caching settings

## Installation

1. Install data_loader dependencies:
```bash
cd data_loader
pip install -r requirements.txt
```

2. Install format_handler dependencies (required for LocalFileLoader):
```bash
cd format_handler
pip install -r requirements.txt
```

## Development

### Running Tests

```bash
pytest tests/
```

## Installation

```bash
pip install -e .
```

## Adding New Data Sources

The module is designed for easy extension. To add a new data source (e.g., GitHub, SharePoint, Azure):

1. Create a new file in `sources/` (e.g., `sources/github.py`)
2. Extend the `BaseLoader` class from `base/loader.py`:
   ```python
   from ..base.loader import BaseLoader
   import pandas as pd
   
   class GitHubLoader(BaseLoader):
       def _load_raw_data(self, source: str, **kwargs) -> pd.DataFrame:
           # Your implementation to load raw data
           # Must return a pandas DataFrame or data convertible to DataFrame
           pass
       
       def validate_source(self, source: str) -> bool:
           # Your implementation to validate source accessibility
           # Return True if valid, False otherwise
           pass
   ```
3. Implement the required abstract methods:
   - `_load_raw_data()`: Load raw data from source (returns DataFrame)
   - `validate_source()`: Validate source accessibility (returns bool)
4. The base class `get_data()` method handles the workflow:
   - Validation (optional)
   - Raw data loading (your implementation)
   - DataFrame conversion
   - Return DataFrame
5. Register the loader in `sources/__init__.py`
6. Add tests in `tests/test_github.py`
7. Update `config.yaml` with any source-specific configuration

## License

[Your License Here]

## Contributing

[Contributing Guidelines Here]

