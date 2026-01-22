"""
Tests for SAS7BDAT format handler.
"""

import pytest
from pathlib import Path
from format_handler.handlers.sas7bdat_handler import SAS7BDATFormatHandler


class TestSAS7BDATFormatHandler:
    """Test cases for SAS7BDATFormatHandler."""
    
    def test_can_handle_sas7bdat_extension(self):
        """Test that handler recognizes .sas7bdat files."""
        handler = SAS7BDATFormatHandler()
        
        assert handler.can_handle('data.sas7bdat') is True
        assert handler.can_handle('DATA.SAS7BDAT') is True
        assert handler.can_handle('file.sas7bdat') is True
        assert handler.can_handle('data.csv') is False
        assert handler.can_handle('data.txt') is False
    
    def test_can_handle_format_hint(self):
        """Test that handler recognizes format hint."""
        handler = SAS7BDATFormatHandler()
        
        assert handler.can_handle('data.txt', format_hint='sas7bdat') is True
        assert handler.can_handle('data.csv', format_hint='sas7bdat') is True
        assert handler.can_handle('data.sas7bdat', format_hint='sas7bdat') is True
        assert handler.can_handle('data.sas7bdat', format_hint='csv') is False
        assert handler.can_handle('data.sas7bdat', format_hint='SAS7BDAT') is True  # Case insensitive
    
    def test_get_supported_extensions(self):
        """Test that handler returns correct extensions."""
        handler = SAS7BDATFormatHandler()
        extensions = handler.get_supported_extensions()
        
        assert '.sas7bdat' in extensions
        assert len(extensions) == 1
    
    def test_get_format_name(self):
        """Test that handler returns correct format name."""
        handler = SAS7BDATFormatHandler()
        format_name = handler.get_format_name()
        
        assert format_name == 'sas7bdat'
    
    def test_config_initialization(self):
        """Test handler initialization with configuration."""
        config = {
            'encoding': 'utf-8',
            'columns': ['col1', 'col2'],
            'chunksize': 1000,
            'iterator': False
        }
        handler = SAS7BDATFormatHandler(config=config)
        
        assert handler.encoding == 'utf-8'
        assert handler.columns == ['col1', 'col2']
        assert handler.chunksize == 1000
        assert handler.iterator is False
    
    def test_config_defaults(self):
        """Test handler initialization with default configuration."""
        handler = SAS7BDATFormatHandler()
        
        assert handler.encoding == 'latin-1'  # Default from config
        assert handler.columns is None
        assert handler.chunksize is None
        assert handler.iterator is False
    
    def test_file_not_found_error(self):
        """Test error handling when file does not exist."""
        handler = SAS7BDATFormatHandler()
        non_existent_file = 'non_existent_file.sas7bdat'
        
        with pytest.raises(FileNotFoundError) as exc_info:
            handler.load(non_existent_file)
        
        assert 'not found' in str(exc_info.value).lower()
        assert non_existent_file in str(exc_info.value)
    
    def test_missing_backend_error(self):
        """Test error handling when pyreadstat is not installed."""
        # Check if pyreadstat is available
        try:
            import pyreadstat
            pytest.skip("pyreadstat is installed, cannot test missing backend error")
        except ImportError:
            pass  # pyreadstat not installed, proceed with test
        
        handler = SAS7BDATFormatHandler()
        
        # Create a dummy file path (won't actually try to read it)
        # The ImportError will be raised when pandas tries to use read_sas
        test_file = Path(__file__).parent.parent.parent / 'TestData' / 'test.sas7bdat'
        
        # If file doesn't exist, we'll get FileNotFoundError first
        # If file exists but pyreadstat is missing, we'll get ImportError
        if test_file.exists():
            with pytest.raises(ImportError) as exc_info:
                handler.load(str(test_file))
            assert 'pyreadstat' in str(exc_info.value).lower()
            assert 'install' in str(exc_info.value).lower()
    
    def test_get_config(self):
        """Test getting handler configuration."""
        config = {'encoding': 'utf-8', 'columns': ['col1']}
        handler = SAS7BDATFormatHandler(config=config)
        
        retrieved_config = handler.get_config()
        assert retrieved_config == config
        # Ensure it's a copy, not a reference
        assert retrieved_config is not config
