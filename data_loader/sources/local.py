"""
Local file loader.

Handles loading from local filesystem including:
- CSV files
- Custom TXT files (with configurable separators)
- Parquet files
- And more...

This loader uses the format_handler module to handle different file formats.
"""

from typing import Any, Dict, Optional, Literal
from pathlib import Path
import pandas as pd
from ..base.loader import BaseLoader
from ..utils.file_finder import resolve_file_path

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
                   - base_directory: Base directory for resolving relative paths/patterns
                                    (default: config file directory)
                   - config_file_path: Path to config file (for resolving base_directory)
        """
        super().__init__(config)
        
        # Initialize format handler registry
        if FORMAT_HANDLER_AVAILABLE and get_default_registry is not None:
            format_config_path = self.config.get('format_handler_config_path')
            # Use default registry which has handlers pre-registered
            self.format_registry = get_default_registry(config_path=format_config_path)
        else:
            self.format_registry = None
        
        # Store base directory and config file path for pattern resolution
        self.base_directory = self.config.get('base_directory')
        self.config_file_path = self.config.get('config_file_path')
        if self.config_file_path is not None:
            self.config_file_path = Path(self.config_file_path)
        
        # Initialize logger here
        # self.logger = setup_logger(__name__, self.config.get('logging', {}))
    
    def _load_raw_data(
        self,
        source: str,
        format: Optional[str] = None,
        match_strategy: Literal["first", "latest", "all"] = "first",
        **kwargs
    ) -> pd.DataFrame:
        """
        Load raw data from a local file.
        
        This method is called by the base class get_data() method.
        It handles the source-specific logic for reading local files using
        the format_handler module.
        
        Supports both exact file paths and glob patterns (e.g., "data_*.csv").
        Patterns are resolved relative to base_directory.
        
        Args:
            source: Path to the local file or glob pattern
            format: Optional explicit format name (e.g., 'csv', 'custom_txt', 'parquet')
                   If not provided, format is auto-detected from file extension
            match_strategy: Strategy for handling multiple pattern matches
                          - "first": First match alphabetically (default)
                          - "latest": Most recently modified file
                          - "all": All matching files (returns concatenated DataFrame)
            **kwargs: Additional parameters passed to format handler
                     (e.g., column_separator, row_separator for custom_txt;
                      engine, columns for parquet; sep, encoding for csv)
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If the file does not exist or no matches found
            ValueError: If the file format is not supported, format_handler is not available,
                       or resolved path is outside base_directory
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
        
        # Resolve source path/pattern to actual file path(s)
        try:
            resolved_path = resolve_file_path(
                source,
                base_directory=self.base_directory,
                config_file_path=self.config_file_path,
                match_strategy=match_strategy
            )
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"File or pattern not found: {source}. "
                f"Base directory: {self.base_directory or 'config file directory'}"
            ) from e
        except ValueError as e:
            # Path validation error (outside base directory)
            raise ValueError(
                f"Path validation failed for '{source}': {e}"
            ) from e
        
        # Handle multiple files if match_strategy is "all"
        if match_strategy == "all" and isinstance(resolved_path, list):
            # Load all matching files and concatenate
            dataframes = []
            for file_path in resolved_path:
                handler = self.format_registry.get_handler(str(file_path), format_override=format)
                df = handler.load(str(file_path), **kwargs)
                dataframes.append(df)
            
            # Concatenate all DataFrames
            import pandas as pd
            return pd.concat(dataframes, ignore_index=True)
        else:
            # Single file (or first/latest from pattern)
            file_path = resolved_path if not isinstance(resolved_path, list) else resolved_path[0]
            
            # Get appropriate format handler
            try:
                handler = self.format_registry.get_handler(str(file_path), format_override=format)
            except ValueError as e:
                raise ValueError(
                    f"Unsupported file format for '{file_path}'. "
                    f"Supported formats: {self.format_registry.list_supported_formats()}"
                ) from e
            
            # Load data using the format handler
            df = handler.load(str(file_path), **kwargs)
            
            return df
    
    def validate_source(self, source: str) -> bool:
        """
        Validate that the local file exists and is accessible.
        
        Supports both exact file paths and glob patterns.
        Patterns are resolved relative to base_directory.
        
        Args:
            source: Path to the local file or glob pattern
        
        Returns:
            True if file exists and is accessible (or pattern matches files), False otherwise
        """
        try:
            # Try to resolve the path/pattern
            resolved_path = resolve_file_path(
                source,
                base_directory=self.base_directory,
                config_file_path=self.config_file_path,
                match_strategy="first"
            )
            
            # Handle list of paths (from "all" strategy)
            if isinstance(resolved_path, list):
                if not resolved_path:
                    return False
                # Validate first match
                file_path = resolved_path[0]
            else:
                file_path = resolved_path
            
            # Check if it's a file (not a directory)
            if not file_path.is_file():
                return False
            
            # Check if file is readable by attempting to open it
            try:
                with open(file_path, 'rb') as f:
                    f.read(1)  # Try to read at least 1 byte to verify readability
                return True
            except (IOError, OSError, PermissionError):
                return False
            
        except (FileNotFoundError, ValueError):
            # File/pattern not found or validation failed
            return False
        except (ValueError, OSError, TypeError):
            # Invalid path or other OS errors
            return False
