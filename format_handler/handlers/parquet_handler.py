"""
Parquet format handler.

Handles loading Parquet files (columnar storage format).
"""

from typing import Any, Dict, List, Optional
import pandas as pd
from pathlib import Path
from ..base.handler import FileFormatHandler


class ParquetFormatHandler(FileFormatHandler):
    """
    Handler for Parquet files.
    
    Parquet is a columnar storage file format optimized for analytics.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Parquet format handler.
        
        Args:
            config: Optional configuration dictionary
                   Supported keys:
                   - engine: Engine to use ('pyarrow' or 'fastparquet', default: 'pyarrow')
                   - columns: List of column names to read (default: None, reads all)
        """
        super().__init__(config)
        self.engine = self.config.get('engine', 'pyarrow')
        self.columns = self.config.get('columns', None)
    
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
            True if source is a Parquet file or format_hint is 'parquet'
        """
        if format_hint and format_hint.lower() == 'parquet':
            return True
        
        if isinstance(source, str):
            return source.lower().endswith(('.parquet', '.pqt'))
        
        return False
    
    def load(
        self,
        source: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from a Parquet file.
        
        Args:
            source: Path to the Parquet file
            **kwargs: Additional parameters for pd.read_parquet()
                     Common parameters:
                     - engine: Engine to use ('pyarrow' or 'fastparquet', overrides config)
                     - columns: List of column names to read (overrides config)
                     - filters: List of filters to apply (for row filtering)
                     - use_pandas_metadata: Use pandas metadata if available
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be parsed as Parquet
            ImportError: If required engine (pyarrow or fastparquet) is not installed
        
        Note:
            Requires either 'pyarrow' or 'fastparquet' package to be installed.
            PyArrow is recommended and is the default engine.
        """
        # Check if file exists
        source_path = Path(source)
        if not source_path.exists():
            raise FileNotFoundError(f"Parquet file not found: {source}")
        
        # Merge config with kwargs (kwargs take precedence)
        read_params = {
            'engine': self.engine,
        }
        
        # Add columns if specified in config
        if self.columns is not None:
            read_params['columns'] = self.columns
        
        read_params.update(kwargs)
        
        try:
            # Read Parquet file
            df = pd.read_parquet(source, **read_params)
            return df
        except ImportError as e:
            # Check if it's a missing engine error
            if 'pyarrow' in str(e).lower() or 'fastparquet' in str(e).lower():
                raise ImportError(
                    f"Parquet engine '{read_params.get('engine', 'pyarrow')}' is not installed. "
                    f"Please install it with: pip install pyarrow (or fastparquet)"
                ) from e
            raise
        except Exception as e:
            raise ValueError(
                f"Failed to load Parquet file '{source}': {str(e)}"
            ) from e
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List containing '.parquet' and '.pqt'
        """
        return ['.parquet', '.pqt']

