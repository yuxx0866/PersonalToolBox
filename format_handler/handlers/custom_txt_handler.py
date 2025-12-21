"""
Custom TXT format handler.

Handles loading TXT files with custom column and row separators.
Supports configurable separators (e.g., *endf* for columns, *endr* for rows).
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from pathlib import Path
from ..base.handler import FileFormatHandler


class CustomTXTFormatHandler(FileFormatHandler):
    """
    Handler for custom TXT files with configurable separators.
    
    Default separators:
    - Column separator: '*endf*'
    - Row separator: '*endr*'
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the custom TXT format handler.
        
        Args:
            config: Optional configuration dictionary
                   Supported keys:
                   - column_separator: Column separator (default: '*endf*')
                   - row_separator: Row separator (default: '*endr*')
                   - encoding: File encoding (default: 'utf-8')
                   - has_header: Whether first row is header (default: True)
                   - strip_whitespace: Strip whitespace from values (default: True)
        """
        super().__init__(config)
        self.column_separator = self.config.get('column_separator', '*endf*')
        self.row_separator = self.config.get('row_separator', '*endr*')
        self.encoding = self.config.get('encoding', 'utf-8')
        self.has_header = self.config.get('has_header', True)
        self.strip_whitespace = self.config.get('strip_whitespace', True)
    
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
            True if source is a TXT file and format_hint is 'custom_txt' or None
        """
        if format_hint:
            return format_hint.lower() in ('custom_txt', 'txt')
        
        if isinstance(source, str):
            return source.lower().endswith('.txt')
        
        return False
    
    def load(
        self,
        source: str,
        column_separator: Optional[str] = None,
        row_separator: Optional[str] = None,
        has_header: Optional[bool] = None,
        strip_whitespace: Optional[bool] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from a custom TXT file.
        
        Args:
            source: Path to the TXT file
            column_separator: Column separator (overrides config)
            row_separator: Row separator (overrides config)
            has_header: Whether first row is header (overrides config)
            strip_whitespace: Strip whitespace from values (overrides config)
            **kwargs: Additional parameters (currently unused)
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be parsed
        
        Note:
            The file format should be:
            - Columns separated by column_separator (default: '*endf*')
            - Rows separated by row_separator (default: '*endr*')
            - Example: "col1*endf*col2*endf*col3*endr*val1*endf*val2*endf*val3*endr*"
        """
        # Check if file exists
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"TXT file not found: {source}")
        
        # Use provided separators or fall back to config
        col_sep = column_separator if column_separator is not None else self.column_separator
        row_sep = row_separator if row_separator is not None else self.row_separator
        has_hdr = has_header if has_header is not None else self.has_header
        strip_ws = strip_whitespace if strip_whitespace is not None else self.strip_whitespace
        
        try:
            # Read file with specified encoding
            with open(source_path, 'r', encoding=self.encoding) as f:
                content = f.read()
            
            # Handle empty file
            if not content.strip():
                return pd.DataFrame()
            
            # Split by row separator to get rows
            rows = content.split(row_sep)
            
            # Filter out empty rows
            rows = [row for row in rows if row.strip()]
            
            if not rows:
                return pd.DataFrame()
            
            # Parse each row
            parsed_rows = []
            for row in rows:
                # Split by column separator
                columns = row.split(col_sep)
                
                # Strip whitespace if requested
                if strip_ws:
                    columns = [col.strip() for col in columns]
                
                parsed_rows.append(columns)
            
            if not parsed_rows:
                return pd.DataFrame()
            
            # Determine if first row is header
            if has_hdr and len(parsed_rows) > 0:
                headers = parsed_rows[0]
                data_rows = parsed_rows[1:]
            else:
                # No header, use default column names
                num_cols = len(parsed_rows[0]) if parsed_rows else 0
                headers = [f'Column_{i+1}' for i in range(num_cols)]
                data_rows = parsed_rows
            
            # Ensure all rows have same number of columns
            # Pad shorter rows with empty strings
            max_cols = len(headers)
            normalized_rows = []
            for row in data_rows:
                normalized_row = list(row[:max_cols])  # Truncate if too long
                normalized_row.extend([''] * (max_cols - len(normalized_row)))  # Pad if too short
                normalized_rows.append(normalized_row)
            
            # Create DataFrame
            df = pd.DataFrame(normalized_rows, columns=headers)
            
            return df
            
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Failed to decode TXT file '{source}' with encoding '{self.encoding}': {str(e)}"
            ) from e
        except Exception as e:
            raise ValueError(
                f"Failed to load custom TXT file '{source}': {str(e)}"
            ) from e
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List containing '.txt'
        """
        return ['.txt']
