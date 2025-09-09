#!/usr/bin/env python3
"""
Column Inspector for SMARD Data
Analyzes the structure and content of the downloaded SMARD CSV files
"""

import pandas as pd
import os

def inspect_csv_file(filename):
    """Inspect a CSV file and show detailed column information"""
    print(f"Inspecting file: {filename}")
    print("=" * 60)
    
    try:
        # Read the CSV file
        df = pd.read_csv(filename, sep=';', decimal=',')
        
        print(f"Shape: {df.shape} (rows, columns)")
        print(f"Column count: {len(df.columns)}")
        print()
        
        print("Column Details:")
        print("-" * 40)
        for i, col in enumerate(df.columns):
            col_name = repr(col)  # This will show hidden characters
            sample_values = df[col].dropna().head(3).tolist()
            null_count = df[col].isnull().sum()
            data_type = df[col].dtype
            
            print(f"Column {i+1}: {col_name}")
            print(f"  Data type: {data_type}")
            print(f"  Null values: {null_count}")
            print(f"  Sample values: {sample_values}")
            print()
        
        print("First 3 rows:")
        print("-" * 40)
        print(df.head(3).to_string())
        
        print(f"\nLast 3 rows:")
        print("-" * 40)
        print(df.tail(3).to_string())
        
        # Check for unnamed columns specifically
        unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
        if unnamed_cols:
            print(f"\nFound unnamed columns: {unnamed_cols}")
            for col in unnamed_cols:
                print(f"Unnamed column '{col}' content sample:")
                print(df[col].value_counts().head(10))
        
    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    """Main function to inspect SMARD CSV files"""
    
    # Look for CSV files in the smard_data directory
    data_dir = "smard_data"
    
    if not os.path.exists(data_dir):
        print(f"Directory '{data_dir}' not found!")
        print("Please run the smart-downloader.py script first.")
        return
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print(f"No CSV files found in '{data_dir}' directory!")
        return
    
    print("Found CSV files:")
    for i, filename in enumerate(csv_files, 1):
        print(f"{i}. {filename}")
    
    print()
    
    # Inspect the complete file first if it exists
    complete_file = "smard_2024_complete.csv"
    complete_path = os.path.join(data_dir, complete_file)
    
    if os.path.exists(complete_path):
        print("Inspecting the complete combined file:")
        inspect_csv_file(complete_path)
        print("\n" + "="*80 + "\n")
    
    # Ask user which file to inspect in detail
    try:
        choice = input(f"Enter number (1-{len(csv_files)}) to inspect a specific file, or 'q' to quit: ").strip()
        
        if choice.lower() == 'q':
            return
        
        file_index = int(choice) - 1
        if 0 <= file_index < len(csv_files):
            selected_file = os.path.join(data_dir, csv_files[file_index])
            print(f"\nDetailed inspection of: {csv_files[file_index]}")
            inspect_csv_file(selected_file)
        else:
            print("Invalid selection!")
            
    except (ValueError, KeyboardInterrupt):
        print("Exiting...")

if __name__ == "__main__":
    main()
