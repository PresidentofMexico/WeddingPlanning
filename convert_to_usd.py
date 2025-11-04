#!/usr/bin/env python3
"""
Currency Conversion Script for Wedding Venue CSVs

This script fetches current GBP→USD and EUR→USD exchange rates and converts
all venue pricing columns to USD, adding or updating USD columns in the CSV files.

Usage:
    python convert_to_usd.py

The script will:
1. Fetch current exchange rates from exchangerate-api.com
2. Process all venue CSV files (englandmore_csv.csv, englandscotland_csv.csv, 
   france_csv.csv, unitedstates_csv.csv)
3. Convert pricing columns to USD
4. Save the updated CSV files with USD columns
"""

import pandas as pd
import requests
import re
import os
from datetime import datetime
import sys

# Exchange rate API configuration
# Using multiple API sources for redundancy
EXCHANGE_RATE_APIS = [
    "https://open.er-api.com/v6/latest/USD",  # Open Exchange Rates API (no auth required)
    "https://api.exchangerate-api.com/v4/latest/USD",  # exchangerate-api.com
]

def fetch_exchange_rates():
    """
    Fetch current exchange rates for GBP and EUR to USD.
    
    Returns:
        dict: Exchange rates with keys 'GBP_to_USD' and 'EUR_to_USD'
    """
    print("Fetching current exchange rates...")
    
    # Try multiple API sources
    for api_url in EXCHANGE_RATE_APIS:
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # API returns rates FROM USD, so we need to calculate TO USD
            # GBP_to_USD = 1 / USD_to_GBP
            usd_to_gbp = data['rates'].get('GBP')
            usd_to_eur = data['rates'].get('EUR')
            
            # Validate rates are positive numbers
            if not usd_to_gbp or not usd_to_eur or usd_to_gbp <= 0 or usd_to_eur <= 0:
                print(f"  Invalid rates from {api_url}: GBP={usd_to_gbp}, EUR={usd_to_eur}")
                continue
            
            rates = {
                'GBP_to_USD': 1 / usd_to_gbp,
                'EUR_to_USD': 1 / usd_to_eur,
                'date': data.get('time_last_update_utc', data.get('date', datetime.now().strftime('%Y-%m-%d')))
            }
            
            print(f"Exchange rates (as of {rates['date']}):")
            print(f"  1 GBP = ${rates['GBP_to_USD']:.4f} USD")
            print(f"  1 EUR = ${rates['EUR_to_USD']:.4f} USD")
            
            return rates
        except requests.exceptions.RequestException as e:
            print(f"  Network error accessing {api_url}: {e}")
            continue
        except (KeyError, ValueError, TypeError) as e:
            print(f"  Invalid data format from {api_url}: {e}")
            continue
    
    # If all APIs fail, use fallback rates
    print("All APIs failed. Using fallback exchange rates...")
    return {
        'GBP_to_USD': 1.27,  # Approximate rate
        'EUR_to_USD': 1.09,  # Approximate rate
        'date': 'fallback'
    }

def extract_numeric_price(value):
    """
    Extract numeric price from a string that may contain currency symbols,
    ranges, or other text.
    
    Args:
        value: String or numeric value from CSV
        
    Returns:
        float or None: Extracted numeric value, or None if not found
    """
    if pd.isna(value):
        return None
    
    # If already numeric, return it
    if isinstance(value, (int, float)):
        return float(value)
    
    # Convert to string and clean up
    value_str = str(value)
    
    # Remove currency symbols and common text
    value_str = value_str.replace('£', '').replace('€', '').replace('$', '')
    value_str = value_str.replace(',', '')
    value_str = value_str.replace('From ', '').replace('from ', '')
    value_str = value_str.replace(' pp', '').replace(' per person', '')
    
    # Extract first number found (handles ranges like "100-200")
    numbers = re.findall(r'\d+(?:\.\d+)?', value_str)
    if numbers:
        return float(numbers[0])
    
    return None

def convert_price_column(df, original_col, new_col, exchange_rate):
    """
    Convert a price column from original currency to USD.
    
    Args:
        df: DataFrame
        original_col: Name of the original price column
        new_col: Name of the new USD column to create
        exchange_rate: Exchange rate to use for conversion
        
    Returns:
        DataFrame: Updated dataframe with new USD column
    """
    if original_col not in df.columns:
        return df
    
    print(f"  Converting {original_col} → {new_col}...")
    
    # Extract numeric values and convert
    numeric_values = df[original_col].apply(extract_numeric_price)
    
    # Convert to USD (None values will remain None)
    usd_values = []
    for val in numeric_values:
        if val is not None:
            usd_values.append(round(val * exchange_rate, 2))
        else:
            usd_values.append(None)
    
    df[new_col] = usd_values
    
    converted_count = df[new_col].notna().sum()
    print(f"    Converted {converted_count}/{len(df)} values")
    
    return df

def process_csv_file(filename, exchange_rates):
    """
    Process a single CSV file and add/update USD price columns.
    
    Args:
        filename: Name of the CSV file to process
        exchange_rates: Dictionary of exchange rates
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(filepath):
        print(f"Warning: {filename} not found, skipping...")
        return
    
    print(f"\nProcessing {filename}...")
    
    # Determine encoding
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    used_encoding = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(filepath, encoding=encoding)
            used_encoding = encoding
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        print(f"  Error: Could not read {filename} with any common encoding")
        return
    
    print(f"  Loaded {len(df)} venues using {used_encoding} encoding")
    
    # Determine currency based on filename or column names
    is_gbp = 'england' in filename.lower() or 'scotland' in filename.lower()
    is_eur = 'france' in filename.lower()
    is_usd = 'united' in filename.lower() or 'usa' in filename.lower() or 'us' in filename.lower()
    
    # Mapping of original columns to USD columns
    conversions = []
    
    if is_gbp:
        # GBP columns for England/Scotland files
        conversions = [
            ('Published Venue Hire / Package (GBP)', 'Published Venue Hire / Package (USD)', exchange_rates['GBP_to_USD']),
            ('Per_Head/Menu From (GBP)', 'Per_Head/Menu From (USD)', exchange_rates['GBP_to_USD']),
            ('Per-Head / Menu From (GBP)', 'Per-Head / Menu From (USD)', exchange_rates['GBP_to_USD']),
            ('Base Price (£)', 'Base Price (USD)', exchange_rates['GBP_to_USD']),
            ('Price per Guest (£)', 'Price per Guest (USD)', exchange_rates['GBP_to_USD']),
        ]
    elif is_eur:
        # EUR columns for France file
        conversions = [
            ('Published Pricing', 'Published Pricing (USD)', exchange_rates['EUR_to_USD']),
            ('Base Price (€)', 'Base Price (USD)', exchange_rates['EUR_to_USD']),
            ('Price per Guest (€)', 'Price per Guest (USD)', exchange_rates['EUR_to_USD']),
        ]
    elif is_usd:
        # USD columns - already in USD, but standardize column names
        conversions = [
            ('Published Venue Hire / Package (GBP)', 'Published Venue Hire / Package (USD)', 1.0),
            ('Per-Head / Menu From (GBP)', 'Per-Head / Menu From (USD)', 1.0),
            ('Base Price ($)', 'Base Price (USD)', 1.0),
            ('Price per Guest ($)', 'Price per Guest (USD)', 1.0),
        ]
    
    # Apply conversions
    for original_col, new_col, rate in conversions:
        df = convert_price_column(df, original_col, new_col, rate)
    
    # Save the updated CSV
    try:
        df.to_csv(filepath, index=False, encoding=used_encoding)
        print(f"  ✓ Updated {filename}")
    except Exception as e:
        print(f"  Error saving {filename}: {e}")

def main():
    """Main function to process all venue CSV files."""
    print("="*60)
    print("Wedding Venue CSV Currency Conversion to USD")
    print("="*60)
    
    # Fetch exchange rates
    exchange_rates = fetch_exchange_rates()
    
    # List of venue CSV files to process
    csv_files = [
        'englandmore_csv.csv',
        'englandscotland_csv.csv',
        'france_csv.csv',
        'unitedstates_csv.csv'
    ]
    
    # Process each file
    for filename in csv_files:
        process_csv_file(filename, exchange_rates)
    
    print("\n" + "="*60)
    print("Conversion complete!")
    print(f"Exchange rates used (date: {exchange_rates['date']}):")
    print(f"  GBP → USD: {exchange_rates['GBP_to_USD']:.4f}")
    print(f"  EUR → USD: {exchange_rates['EUR_to_USD']:.4f}")
    print("="*60)
    print("\nTo update the dashboard with USD prices, restart the Streamlit app.")
    print("To refresh exchange rates in the future, run this script again:")
    print("  python convert_to_usd.py")

if __name__ == '__main__':
    main()
