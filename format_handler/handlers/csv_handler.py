"""
CSV format handler.

Handles loading CSV files with comma separator.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from pathlib import Path
from ..base.handler import FileFormatHandler


class CSVFormatHandler(FileFormatHandler):
    """
    Handler for CSV (Comma-Separated Values) files.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the CSV format handler.
        
        Args:
            config: Optional configuration dictionary
                   Supported keys:
                   - separator: Column separator (default: ',')
                   - encoding: File encoding (default: 'utf-8')
        """
        super().__init__(config)
        self.separator = self.config.get('separator', ',')
        self.encoding = self.config.get('encoding', 'utf-8')
    
    def can_handle(
        self,
        source: str,
        format_hint: Optional[str] = None
    ) -> bool:
        """
        Check if this handler can process the source.
        
        Args:
            source: File path
            format_hint: Optional explicit format hint
        
        Returns:
            True if source is a CSV file or format_hint is 'csv'
        """
        if format_hint and format_hint.lower() == 'csv':
            return True
        
        if isinstance(source, str):
            return source.lower().endswith('.csv')
        
        return False
    
    def load(
        self,
        source: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from a CSV file.
        
        Args:
            source: Path to the CSV file
            **kwargs: Additional parameters for pd.read_csv()
                     Common parameters:
                     - sep: Column separator (overrides config)
                     - encoding: File encoding (overrides config)
                     - header: Row to use as column names (default: 0)
                     - skiprows: Number of rows to skip
                     - nrows: Number of rows to read
                     - dtype: Data types for columns
                     - na_values: Additional strings to recognize as NA
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be parsed as CSV
            pd.errors.EmptyDataError: If the file is empty
        """
        # Check if file exists
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"CSV file not found: {source}")
        
        # Merge config with kwargs (kwargs take precedence)
        read_params = {
            'sep': self.separator,
            'encoding': self.encoding,
        }
        read_params.update(kwargs)
        
        try:
            # Read CSV file
            df = pd.read_csv(source, **read_params)
            return df
        except pd.errors.EmptyDataError:
            # Return empty DataFrame if file is empty
            return pd.DataFrame()
        except Exception as e:
            raise ValueError(
                f"Failed to load CSV file '{source}': {str(e)}"
            ) from e
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List containing '.csv'
        """
        return ['.csv']
