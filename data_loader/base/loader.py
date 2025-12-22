"""
Abstract base class for all data loaders.

This module defines the interface that all data source loaders must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import pandas as pd


class BaseLoader(ABC):
    """
    Abstract base class for all data loaders.
    
    All data source loaders should inherit from this class and implement
    the required abstract methods.
    
    Design Principles:
    - Single Responsibility: Only loads data, does not transform it
    - Type Safety: Always returns pandas DataFrame
    - Validation: Separates source validation from data validation
    - Template Method: Common workflow in get_data(), source-specific in _load_raw_data()
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the loader.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = None  # Will be initialized by subclasses
    
    def get_data(
        self,
        source: str,
        validate_before_load: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from the source and return as pandas DataFrame.
        
        This method implements the common workflow for all loaders:
        1. Optionally validate source accessibility
        2. Load raw data (source-specific, implemented by subclasses)
        3. Convert to DataFrame if needed
        4. Return DataFrame
        
        This method always returns a pandas DataFrame, even if the source
        contains no data (returns empty DataFrame).
        
        Args:
            source: Source identifier (path, URL, etc.)
            validate_before_load: If True, validates source before loading.
                                 Set to False to skip validation for performance.
            **kwargs: Additional source-specific parameters passed to _load_raw_data()
        
        Returns:
            pandas DataFrame containing the loaded data
        
        Raises:
            FileNotFoundError: If source file/path doesn't exist
            ValueError: If source format is invalid or unsupported, or if data
                       cannot be converted to DataFrame
            pd.errors.EmptyDataError: If source contains no data (optional)
        
        Example:
            >>> loader = LocalFileLoader()
            >>> df = loader.get_data('data.csv')
            >>> # Or skip validation for performance:
            >>> df = loader.get_data('data.csv', validate_before_load=False)
        """
        # Step 1: Validate source (optional)
        if validate_before_load:
            if not self.validate_source(source):
                raise ValueError(f"Source validation failed for: {source}")
        
        # Step 2: Load raw data (source-specific, implemented by subclasses)
        raw_data = self._load_raw_data(source, **kwargs)
        
        # Step 3: Convert to DataFrame if needed
        df = self._ensure_dataframe(raw_data)
        
        # Step 4: Return DataFrame
        return df
    
    @abstractmethod
    def _load_raw_data(
        self,
        source: str,
        **kwargs
    ) -> Any:
        """
        Load raw data from the source (source-specific implementation).
        
        This method is called by get_data() and should contain the source-specific
        logic for loading data. It can return:
        - pandas DataFrame (preferred, no conversion needed)
        - dict, list, or other structures that can be converted to DataFrame
        - File-like objects, bytes, or strings that can be read into DataFrame
        
        Args:
            source: Source identifier (path, URL, etc.)
            **kwargs: Additional source-specific parameters
        
        Returns:
            Raw data in any format that can be converted to DataFrame
        
        Raises:
            FileNotFoundError: If source file/path doesn't exist
            ValueError: If source format is invalid or unsupported
            ConnectionError: If unable to connect to remote source
        
        Note:
            Subclasses must implement this method with source-specific logic.
            For example:
            - LocalFileLoader: Use pd.read_csv(), pd.read_excel(), etc.
            - GitHubLoader: Download file, then read with pandas
            - SharePointLoader: Authenticate, download, then read
        """
        raise NotImplementedError("Subclasses must implement _load_raw_data()")
    
    def _ensure_dataframe(self, data: Any) -> pd.DataFrame:
        """
        Convert data to pandas DataFrame if needed.
        
        This helper method ensures that whatever _load_raw_data() returns
        is converted to a pandas DataFrame. Handles common data types.
        
        Args:
            data: Data in any format (DataFrame, dict, list, etc.)
        
        Returns:
            pandas DataFrame
        
        Raises:
            ValueError: If data cannot be converted to DataFrame
            TypeError: If data type is not supported
        """
        # Already a DataFrame
        if isinstance(data, pd.DataFrame):
            return data
        
        # Empty data - return empty DataFrame
        if data is None:
            return pd.DataFrame()
        
        # Dictionary - convert to DataFrame
        if isinstance(data, dict):
            # If dict of lists/arrays (like {'col1': [1,2,3], 'col2': [4,5,6]})
            if all(isinstance(v, (list, tuple)) for v in data.values()):
                return pd.DataFrame(data)
            # If single row dict, wrap in list
            else:
                return pd.DataFrame([data])
        
        # List of dicts
        if isinstance(data, list):
            if len(data) == 0:
                return pd.DataFrame()
            # List of dicts
            if isinstance(data[0], dict):
                return pd.DataFrame(data)
            # List of lists (assume first list is headers if provided)
            elif isinstance(data[0], (list, tuple)):
                # Try to infer if first row is headers
                if len(data) > 1:
                    return pd.DataFrame(data[1:], columns=data[0] if data[0] else None)
                else:
                    return pd.DataFrame(data)
            # Simple list - create single column DataFrame
            else:
                return pd.DataFrame(data)
        
        # String or bytes - try to read as CSV
        if isinstance(data, (str, bytes)):
            import io
            if isinstance(data, bytes):
                data = io.BytesIO(data)
            else:
                data = io.StringIO(data)
            try:
                return pd.read_csv(data)
            except Exception:
                raise ValueError(
                    "String/bytes data could not be parsed as CSV. "
                    "Consider preprocessing the data in _load_raw_data()."
                )
        
        # File-like object
        if hasattr(data, 'read'):
            try:
                return pd.read_csv(data)
            except Exception:
                raise ValueError(
                    "File-like object could not be read as CSV. "
                    "Consider preprocessing the data in _load_raw_data()."
                )
        
        # Unsupported type
        raise TypeError(
            f"Cannot convert {type(data).__name__} to DataFrame. "
            f"Return a DataFrame, dict, list, or file-like object from _load_raw_data()."
        )
    
    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """
        Validate that the source is accessible and valid.
        
        This validates the source itself (file exists, URL accessible, etc.),
        not the data structure. For data structure validation, use validate_schema().
        
        Args:
            source: Source identifier to validate
        
        Returns:
            True if source is valid and accessible, False otherwise
        
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement validate_source()")
    
    def validate_schema(
        self,
        df: pd.DataFrame,
        required_columns: Optional[List[str]] = None,
        column_types: Optional[Dict[str, type]] = None,
        allow_extra_columns: bool = True,
        allow_empty: bool = False
    ) -> bool:
        """
        Validate the structure of a loaded DataFrame.
        
        This method provides basic schema validation. For complex validation
        (business rules, data quality checks), implement separate validation
        logic outside the loader.
        
        Args:
            df: DataFrame to validate
            required_columns: List of column names that must be present.
                             If None, no column name validation is performed.
            column_types: Dictionary mapping column names to expected types.
                         Example: {'id': int, 'name': str, 'price': float}
                         If None, no type validation is performed.
            allow_extra_columns: If True, allows columns not in required_columns.
                                If False, raises ValueError for extra columns.
            allow_empty: If True, allows empty DataFrames. If False, raises
                        ValueError for empty DataFrames.
        
        Returns:
            True if DataFrame structure is valid
        
        Raises:
            ValueError: If validation fails (missing columns, wrong types, etc.)
            TypeError: If df is not a DataFrame
        
        Example:
            >>> loader = LocalFileLoader()
            >>> df = loader.get_data('data.csv')
            >>> loader.validate_schema(
            ...     df,
            ...     required_columns=['id', 'name', 'date'],
            ...     column_types={'id': int, 'date': 'datetime64[ns]'}
            ... )
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        # Check if DataFrame is empty
        if not allow_empty and df.empty:
            raise ValueError("DataFrame is empty but allow_empty=False")
        
        # Validate required columns
        if required_columns is not None:
            df_columns = set(df.columns)
            required_set = set(required_columns)
            
            # Check for missing columns
            missing = required_set - df_columns
            if missing:
                raise ValueError(
                    f"Missing required columns: {sorted(missing)}. "
                    f"Found columns: {sorted(df_columns)}"
                )
            
            # Check for extra columns if not allowed
            if not allow_extra_columns:
                extra = df_columns - required_set
                if extra:
                    raise ValueError(
                        f"Unexpected columns found: {sorted(extra)}. "
                        f"Expected only: {sorted(required_set)}"
                    )
        
        # Validate column types
        if column_types is not None:
            for col_name, expected_type in column_types.items():
                if col_name not in df.columns:
                    continue  # Skip if column not present (already checked above)
                
                actual_type = df[col_name].dtype
                
                # Handle special cases for pandas dtypes
                if expected_type == int:
                    if not pd.api.types.is_integer_dtype(actual_type):
                        raise ValueError(
                            f"Column '{col_name}' expected integer type, "
                            f"got {actual_type}"
                        )
                elif expected_type == float:
                    if not pd.api.types.is_float_dtype(actual_type):
                        raise ValueError(
                            f"Column '{col_name}' expected float type, "
                            f"got {actual_type}"
                        )
                elif expected_type == str:
                    if not pd.api.types.is_string_dtype(actual_type) and not pd.api.types.is_object_dtype(actual_type):
                        raise ValueError(
                            f"Column '{col_name}' expected string type, "
                            f"got {actual_type}"
                        )
                elif isinstance(expected_type, str):
                    # Handle string type specifications like 'datetime64[ns]'
                    if expected_type.startswith('datetime'):
                        if not pd.api.types.is_datetime64_any_dtype(actual_type):
                            raise ValueError(
                                f"Column '{col_name}' expected datetime type, "
                                f"got {actual_type}"
                            )
                    elif actual_type != expected_type:
                        raise ValueError(
                            f"Column '{col_name}' expected type {expected_type}, "
                            f"got {actual_type}"
                        )
                elif actual_type != expected_type:
                    raise ValueError(
                        f"Column '{col_name}' expected type {expected_type}, "
                        f"got {actual_type}"
                    )
        
        return True
    
    def get_metadata(self, source: str) -> Dict:
        """
        Get metadata about the source.
        
        Args:
            source: Source identifier
        
        Returns:
            Dictionary containing metadata (size, type, last_modified, etc.)
        
        Note:
            This method can be overridden by subclasses for source-specific metadata
        """
        return {}
