import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Function to save raw data to a CSV file
def save_raw_data(df: pd.DataFrame, filename: str):
    """
    Save the raw DataFrame to a CSV file without any processing.

    Parameters:
    - df (pd.DataFrame): The raw scraped data.
    - filename (str): The name of the output CSV file.
    """
    try:
        df.to_csv(filename, index=False)
        logging.info(f"Raw data saved to {filename} successfully.")
    except Exception as e:
        logging.error(f"Failed to save raw data to {filename}: {e}")


# Function to validate columns in the DataFrame
def validate_columns(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Validate that all required columns are present in the DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame to validate.
    - required_columns (list): List of required column names.

    Returns:
    - bool: True if all required columns are present, False otherwise.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"Missing columns in data: {missing_columns}")
        return False
    return True


# Function to perform basic cleaning on the raw data
def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform basic cleaning on the raw scraped data without altering the datetime.

    - Replace empty strings with NaN and fill with 'N/A'.

    Parameters:
    - df (pd.DataFrame): The raw scraped data.

    Returns:
    - pd.DataFrame: Cleaned data.
    """
    try:
        df = df.copy()

        required_columns = ['year', 'date', 'time', 'currency', 'impact', 'event', 'actual', 'forecast', 'previous']
        if not validate_columns(df, required_columns):
            return pd.DataFrame()

        # Replace empty strings with NaN and fill with 'N/A'
        df.replace('', pd.NA, inplace=True)
        df.fillna('N/A', inplace=True)

        logging.info("Basic data cleaning completed successfully.")
        return df

    except Exception as e:
        logging.error(f"An error occurred during basic data cleaning: {e}")
        return pd.DataFrame()
