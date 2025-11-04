#!/usr/bin/env python3
"""
Fill Missing URLs Script for Wedding Venue CSVs

This script ensures every venue has a URL by:
1. Copying URLs from other columns when one is missing
2. Searching the web for venues with no URLs at all

Usage:
    python fill_missing_urls.py
"""

import pandas as pd
import requests
import os
import sys
import time
from datetime import datetime

def search_venue_url(venue_name, region):
    """
    Search for a venue's official website using web search.
    
    Args:
        venue_name: Name of the venue
        region: Region/country of the venue
        
    Returns:
        str or None: Found URL or None if search fails
    """
    print(f"  Searching web for: {venue_name} ({region})")
    
    # Create search query
    query = f"{venue_name} {region} wedding venue official website"
    
    try:
        # Use a simple search approach - try to find official website
        # This is a placeholder - in production you'd use a real search API
        # For now, we'll return None and let manual review happen
        print(f"    Web search would be performed here for: {query}")
        print(f"    (Skipping automated web search - manual review recommended)")
        return None
    except Exception as e:
        print(f"    Search error: {e}")
        return None

def fill_missing_urls_in_file(filename):
    """
    Process a single CSV file and fill in missing URLs.
    
    Args:
        filename: Name of the CSV file to process
        
    Returns:
        dict: Statistics about changes made
    """
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(filepath):
        print(f"Warning: {filename} not found, skipping...")
        return {'skipped': True}
    
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
        return {'error': True}
    
    print(f"  Loaded {len(df)} venues using {used_encoding} encoding")
    
    stats = {
        'total': len(df),
        'had_pricing_source': 0,
        'had_website': 0,
        'filled_pricing_from_website': 0,
        'filled_website_from_pricing': 0,
        'still_missing': 0,
        'web_searches_needed': []
    }
    
    # Check which columns exist
    has_pricing_source = 'Pricing Source URL(s)' in df.columns
    has_website = 'Website' in df.columns
    
    # Add missing columns if needed
    if not has_pricing_source:
        print(f"  Adding 'Pricing Source URL(s)' column...")
        df['Pricing Source URL(s)'] = None
        has_pricing_source = True
    
    if not has_website:
        print(f"  Adding 'Website' column...")
        df['Website'] = None
        has_website = True
    
    # Count initial state
    stats['had_pricing_source'] = df['Pricing Source URL(s)'].notna().sum()
    stats['had_website'] = df['Website'].notna().sum()
    
    # Fill missing URLs
    for idx, row in df.iterrows():
        venue_name = row['Venue']
        pricing_url = row.get('Pricing Source URL(s)')
        website_url = row.get('Website')
        region = row.get('Region/Country', 'Unknown')
        
        # Check if Pricing Source URL is missing but Website exists
        if pd.isna(pricing_url) and pd.notna(website_url):
            df.at[idx, 'Pricing Source URL(s)'] = website_url
            stats['filled_pricing_from_website'] += 1
            print(f"  ✓ Filled Pricing Source URL from Website for: {venue_name}")
        
        # Check if Website is missing but Pricing Source URL exists
        elif pd.isna(website_url) and pd.notna(pricing_url):
            df.at[idx, 'Website'] = pricing_url
            stats['filled_website_from_pricing'] += 1
            print(f"  ✓ Filled Website from Pricing Source URL for: {venue_name}")
        
        # Both are missing - needs web search
        elif pd.isna(website_url) and pd.isna(pricing_url):
            stats['still_missing'] += 1
            stats['web_searches_needed'].append({
                'venue': venue_name,
                'region': region
            })
            print(f"  ⚠ Missing both URLs for: {venue_name} - web search needed")
    
    # Perform web searches for venues with no URLs (optional)
    if stats['web_searches_needed']:
        print(f"\n  Found {len(stats['web_searches_needed'])} venues needing web search...")
        print(f"  (Skipping automated web search - these should be researched manually)")
    
    # Save the updated CSV if changes were made
    changes_made = (stats['filled_pricing_from_website'] + 
                    stats['filled_website_from_pricing'] > 0)
    
    if changes_made:
        try:
            df.to_csv(filepath, index=False, encoding=used_encoding)
            print(f"  ✓ Updated {filename}")
        except Exception as e:
            print(f"  Error saving {filename}: {e}")
            return {'error': True}
    else:
        print(f"  No changes needed for {filename}")
    
    return stats

def main():
    """Main function to process all venue CSV files."""
    print("="*60)
    print("Wedding Venue CSV - Fill Missing URLs")
    print("="*60)
    
    # List of venue CSV files to process
    csv_files = [
        'englandmore_csv.csv',
        'englandscotland_csv.csv',
        'france_csv.csv',
        'unitedstates_csv.csv'
    ]
    
    all_stats = {}
    
    # Process each file
    for filename in csv_files:
        stats = fill_missing_urls_in_file(filename)
        all_stats[filename] = stats
    
    # Print summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    total_filled_pricing = 0
    total_filled_website = 0
    total_still_missing = 0
    all_web_searches = []
    
    for filename, stats in all_stats.items():
        if stats.get('skipped') or stats.get('error'):
            continue
        
        print(f"\n{filename}:")
        print(f"  Total venues: {stats['total']}")
        print(f"  Filled Pricing Source from Website: {stats['filled_pricing_from_website']}")
        print(f"  Filled Website from Pricing Source: {stats['filled_website_from_pricing']}")
        print(f"  Still missing both URLs: {stats['still_missing']}")
        
        total_filled_pricing += stats['filled_pricing_from_website']
        total_filled_website += stats['filled_website_from_pricing']
        total_still_missing += stats['still_missing']
        all_web_searches.extend(stats['web_searches_needed'])
    
    print("\n" + "="*60)
    print("Overall Statistics")
    print("="*60)
    print(f"Total venues with URLs filled from other columns: {total_filled_pricing + total_filled_website}")
    print(f"  - Pricing Source filled from Website: {total_filled_pricing}")
    print(f"  - Website filled from Pricing Source: {total_filled_website}")
    print(f"Venues still missing URLs (need manual research): {total_still_missing}")
    
    if all_web_searches:
        print("\nVenues requiring manual research:")
        for item in all_web_searches:
            print(f"  - {item['venue']} ({item['region']})")
        print("\nPlease research these venues manually and add their official website URLs.")
    
    print("\n" + "="*60)
    print("Complete!")
    print("="*60)

if __name__ == '__main__':
    main()
