"""
SAS7BDAT format handler.

Handles loading SAS7BDAT files (SAS binary data format).
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from pathlib import Path
from ..base.handler import FileFormatHandler


class SAS7BDATFormatHandler(FileFormatHandler):
    """
    Handler for SAS7BDAT files.
    
    SAS7BDAT is a binary file format used by SAS (Statistical Analysis System).
    This handler uses pandas.read_sas() which requires pyreadstat as a backend.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the SAS7BDAT format handler.
        
        Args:
            config: Optional configuration dictionary
                   Supported keys:
                   - encoding: Character encoding (default: 'latin-1')
                   - columns: List of column names to read (default: None, reads all)
                   - chunksize: Number of rows to read at a time (default: None)
                   - iterator: Return iterator for chunked reading (default: False)
        """
        super().__init__(config)
        self.encoding = self.config.get('encoding', 'latin-1')
        self.columns = self.config.get('columns', None)
        self.chunksize = self.config.get('chunksize', None)
        self.iterator = self.config.get('iterator', False)
    
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
            True if source is a SAS7BDAT file or format_hint is 'sas7bdat'
        """
        if format_hint and format_hint.lower() == 'sas7bdat':
            return True
        
        if isinstance(source, str):
            return source.lower().endswith('.sas7bdat')
        
        return False
    
    def load(
        self,
        source: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from a SAS7BDAT file.
        
        Args:
            source: Path to the SAS7BDAT file
            **kwargs: Additional parameters for pd.read_sas()
                     Common parameters:
                     - encoding: File encoding (overrides config)
                     - columns: List of column names to read (overrides config)
                     - chunksize: Number of rows to read at a time (overrides config)
                     - iterator: Return iterator for chunked reading (overrides config)
                     - format: Format type (default: 'sas7bdat')
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If the file does not exist
            ImportError: If pyreadstat backend is not installed
            ValueError: If the file cannot be parsed as SAS7BDAT
        
        Note:
            Requires 'pyreadstat' package to be installed.
            Install with: pip install pyreadstat
            Pandas will automatically use pyreadstat if available.
        """
        # Check if file exists
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"SAS7BDAT file not found: {source}")
        
        # Merge config with kwargs (kwargs take precedence)
        read_params = {
            'format': 'sas7bdat',
            'encoding': self.encoding,
        }
        
        # Add columns if specified in config
        if self.columns is not None:
            read_params['columns'] = self.columns
        
        # Add chunksize if specified in config
        if self.chunksize is not None:
            read_params['chunksize'] = self.chunksize
        
        # Add iterator if specified in config
        if self.iterator:
            read_params['iterator'] = self.iterator
        
        read_params.update(kwargs)
        
        try:
            # Read SAS7BDAT file using pandas
            # Pandas will automatically detect and use pyreadstat if available
            df = pd.read_sas(source, **read_params)
            return df
        except ImportError as e:
            # Pandas will raise ImportError if pyreadstat is not available
            if 'pyreadstat' in str(e).lower() or 'sas7bdat' in str(e).lower():
                raise ImportError(
                    "SAS7BDAT support requires 'pyreadstat'. "
                    "Install with: pip install pyreadstat"
                ) from e
            raise
        except Exception as e:
            raise ValueError(
                f"Failed to load SAS7BDAT file '{source}': {str(e)}"
            ) from e
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List containing '.sas7bdat'
        """
        return ['.sas7bdat']
