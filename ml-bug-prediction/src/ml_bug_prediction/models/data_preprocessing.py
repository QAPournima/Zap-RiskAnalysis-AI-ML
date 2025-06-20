import pandas as pd
import os

def preprocess_data(input_path, output_path='data/processed/processed_data.csv'):
    """
    Loads raw data, fills missing values, and saves the cleaned data.
    """
    # Load the raw data
    df = pd.read_csv(input_path)
    print("Loaded data shape:", df.shape)

    # Fill missing values with 0 or a suitable value
    df = df.fillna(0)

    # Example: Convert categorical columns to string (if any)
    # for col in ['Developer']:
    #     if col in df.columns:
    #         df[col] = df[col].astype(str)

    # Save the processed data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")

# Example usage (uncomment to run directly)
# preprocess_data('data/raw/your_data.csv')