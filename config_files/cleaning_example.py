import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series

# --- RULE: Schema-First Validation ---
# Define what "Clean" looks like before writing code.
class CleanSchema(pa.SchemaModel):
    """Schema definition for the cleaned customer dataset."""
    
    user_id: Series[int] = pa.Field(unique=True, ge=0)
    age: Series[int] = pa.Field(ge=0, le=120, nullable=False)
    income: Series[float] = pa.Field(ge=0, nullable=False)
    # Business Rule: Email must be a string (if we had it)
    
    class Config:
        strict = True  # Crash if unexpected columns appear

# --- RULE: No Global Scope ---
# Bad: df = pd.read_csv(...) here at top level.
# Good: Logic is encapsulated in functions below.

def clean_customer_data(df: pd.DataFrame) -> DataFrame[CleanSchema]:
    """
    Cleans raw customer data and enforces schema validation.

    Args:
        df (pd.DataFrame): Raw dataframe containing user_id, age, income.

    Returns:
        DataFrame[CleanSchema]: Validated, clean dataframe.

    Raises:
        pa.errors.SchemaError: If output data violates business rules.
    """
    # 1. Copy data to avoid SettingWithCopy warnings
    clean_df = df.copy()

    # 2. Handle Missing Values
    clean_df = clean_df.dropna(subset=['income'])

    # 3. Handle Business Logic (Age > 0 and < 120)
    clean_df = clean_df[
        (clean_df['age'] > 0) & 
        (clean_df['age'] < 120)
    ]

    # 4. Enforce Types
    clean_df['age'] = clean_df['age'].astype(int)
    clean_df['income'] = clean_df['income'].astype(float)

    # 5. Validate Output against Schema
    # This will throw an error if we missed anything
    return CleanSchema.validate(clean_df)

if __name__ == "__main__":
    # This block allows you to run the script manually for debugging
    # But prevents it from running when imported by tests.
    pass