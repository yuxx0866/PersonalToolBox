"""
Local file loader.

Handles loading from local filesystem including:
- CSV files
- Custom TXT files (with configurable separators)
- Parquet files
- And more...

This loader uses the format_handler module to handle different file formats.
"""

from typing import Any, Dict, Optional
from pathlib import Path
import pandas as pd
from ..base.loader import BaseLoader

# Import format_handler module with graceful fallback
try:
    from format_handler import get_default_registry, FormatRegistry
    FORMAT_HANDLER_AVAILABLE = True
except ImportError:
    FORMAT_HANDLER_AVAILABLE = False
    FormatRegistry = None
    get_default_registry = None


class LocalFileLoader(BaseLoader):
    """
    Loader for local filesystem files.
    
    Uses the format_handler module to support various file formats including:
    - CSV files
    - Custom TXT files (with *endf* and *endr* separators)
    - Parquet files
    
    The loader automatically detects file format from extension or accepts
    explicit format specification via the format parameter.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the local file loader.
        
        Args:
            config: Optional configuration dictionary
                   Supported keys:
                   - format_handler_config_path: Path to format_handler config file
        """
        super().__init__(config)
        
        # Initialize format handler registry
        if FORMAT_HANDLER_AVAILABLE and get_default_registry is not None:
            format_config_path = self.config.get('format_handler_config_path')
            # Use default registry which has handlers pre-registered
            self.format_registry = get_default_registry(config_path=format_config_path)
        else:
            self.format_registry = None
        
        # Initialize logger here
        # self.logger = setup_logger(__name__, self.config.get('logging', {}))
    
    def _load_raw_data(
        self,
        source: str,
        format: Optional[str] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load raw data from a local file.
        
        This method is called by the base class get_data() method.
        It handles the source-specific logic for reading local files using
        the format_handler module.
        
        Args:
            source: Path to the local file
            format: Optional explicit format name (e.g., 'csv', 'custom_txt', 'parquet')
                   If not provided, format is auto-detected from file extension
            **kwargs: Additional parameters passed to format handler
                     (e.g., column_separator, row_separator for custom_txt;
                      engine, columns for parquet; sep, encoding for csv)
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file format is not supported or format_handler is not available
            ImportError: If format_handler module is not installed
        
        Note:
            This method uses the format_handler module to load files.
            Make sure format_handler is installed and accessible.
        """
        if not FORMAT_HANDLER_AVAILABLE:
            raise ImportError(
                "format_handler module is not available. "
                "Please install it or ensure it's in your Python path."
            )
        
        if self.format_registry is None:
            raise ValueError(
                "Format registry is not initialized. "
                "format_handler module may not be properly installed."
            )
        
        # Get appropriate format handler
        try:
            handler = self.format_registry.get_handler(source, format_override=format)
        except ValueError as e:
            raise ValueError(
                f"Unsupported file format for '{source}'. "
                f"Supported formats: {self.format_registry.list_supported_formats()}"
            ) from e
        
        # Load data using the format handler
        df = handler.load(source, **kwargs)
        
        return df
    
    def validate_source(self, source: str) -> bool:
        """
        Validate that the local file exists and is accessible.
        
        Args:
            source: Path to the local file
        
        Returns:
            True if file exists and is accessible, False otherwise
        """
        try:
            source_path = Path(source)
            
            # Check if file exists
            if not source_path.exists():
                return False
            
            # Check if it's a file (not a directory)
            if not source_path.is_file():
                return False
            
            # Check if file is readable by attempting to open it
            try:
                with open(source_path, 'rb') as f:
                    f.read(1)  # Try to read at least 1 byte to verify readability
                return True
            except (IOError, OSError, PermissionError):
                return False
            
        except (ValueError, OSError, TypeError):
            # Invalid path or other OS errors
            return False
