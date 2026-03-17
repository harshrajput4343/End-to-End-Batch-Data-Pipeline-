import pandas as pd
import os

def ingest_data(input_path, output_path):
    print(f"Reading data from {input_path}...")
    
    # Load data
    df = pd.read_csv(input_path)
    
    # Cleaning: Handle nulls
    initial_count = len(df)
    df = df.dropna(subset=['user_id', 'event_type'])
    print(f"Dropped {initial_count - len(df)} rows with nulls.")
    
    # Cleaning: Type casting & validation
    df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce').fillna(0).astype(int)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Drop rows with invalid timestamps
    df = df.dropna(subset=['timestamp'])
    print(f"Cleaned data has {len(df)} rows.")
    
    # Save cleaned data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")

if __name__ == "__main__":
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    INPUT = os.path.join(PROJECT_ROOT, 'data', 'raw_events.csv')
    OUTPUT = os.path.join(PROJECT_ROOT, 'data', 'cleaned_events.csv')
    ingest_data(INPUT, OUTPUT)
