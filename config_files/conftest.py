import pytest
import pandas as pd

# RULE: Fixture-Based Testing
# Tests must rely on this generated data, never on 'C:/Users/...'

@pytest.fixture
def mock_raw_data():
    """
    Generates a synthetic DataFrame that mimics the raw input.
    Includes messy data to test robustness.
    """
    return pd.DataFrame({
        "user_id": [101, 102, 103, 104],
        "age": [25, 40, -5, 150],       # Note: -5 and 150 are dirty data
        "income": [50000, 100000, None, 20000], # Note: None is missing data
        "signup_date": ["2023-01-01", "2023-06-15", "invalid_date", "2023-02-20"]
    })

@pytest.fixture
def mock_clean_data():
    """
    Generates what the data SHOULD look like after cleaning.
    """
    return pd.DataFrame({
        "user_id": [101, 102, 104],     # 103 removed (bad data)
        "category": ["Young", "Adult", "Young"]
    })