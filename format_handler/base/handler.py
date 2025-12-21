"""
Abstract base class for all file format handlers.

This module defines the interface that all format handlers must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd


class FileFormatHandler(ABC):
    """
    Abstract base class for all file format handlers.
    
    All format handlers should inherit from this class and implement
    the required abstract methods.
    
    Design Principles:
    - Single Responsibility: Each handler handles one format
    - Type Safety: Always returns pandas DataFrame
    - Configurable: Supports configuration for format-specific options
    - Extensible: Easy to add new formats
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the format handler.
        
        Args:
            config: Optional configuration dictionary for format-specific settings
        """
        self.config = config or {}
    
    @abstractmethod
    def can_handle(
        self,
        source: str,
        format_hint: Optional[str] = None
    ) -> bool:
        """
        Check if this handler can process the given source.
        
        Args:
            source: File path or identifier
            format_hint: Optional explicit format hint (e.g., 'csv', 'custom_txt')
        
        Returns:
            True if this handler can process the source, False otherwise
        """
        raise NotImplementedError("Subclasses must implement can_handle()")
    
    @abstractmethod
    def load(
        self,
        source: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from the source and return as pandas DataFrame.
        
        Args:
            source: File path or file-like object
            **kwargs: Format-specific parameters (e.g., separator, encoding)
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If source file doesn't exist
            ValueError: If source format is invalid or unsupported
            pd.errors.EmptyDataError: If source contains no data (optional)
        """
        raise NotImplementedError("Subclasses must implement load()")
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of file extensions this handler supports.
        
        Returns:
            List of file extensions (e.g., ['.csv', '.txt'])
        """
        raise NotImplementedError("Subclasses must implement get_supported_extensions()")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get handler-specific configuration.
        
        Returns:
            Dictionary containing handler configuration
        """
        return self.config.copy()
    
    def get_format_name(self) -> str:
        """
        Get the name of the format this handler supports.
        
        Converts CamelCase class name to snake_case format name.
        Examples:
        - CSVFormatHandler -> 'csv'
        - CustomTXTFormatHandler -> 'custom_txt'
        - ParquetFormatHandler -> 'parquet'
        
        Returns:
            Format name in snake_case (e.g., 'csv', 'custom_txt', 'excel')
        """
        import re
        
        # Remove 'FormatHandler' suffix
        class_name = self.__class__.__name__.replace('FormatHandler', '')
        
        # Convert CamelCase to snake_case
        # Insert underscore before uppercase letters (except the first one)
        # Then convert to lowercase
        snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        
        return snake_case

