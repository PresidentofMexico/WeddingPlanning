import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import random
import re
import os
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Wedding Planning Dashboard",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 20px;
        padding-right: 20px;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.2);
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Data directory for storing uploaded files
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Default data files (from repo root)
DEFAULT_GUEST_FILE = 'wedding_roster_csv.csv'
DEFAULT_ENGLAND_SCOTLAND_FILE = 'englandscotland_csv.csv'
DEFAULT_FRANCE_FILE = 'france_csv.csv'

def load_csv_or_excel(file_path, sheet_name=None):
    """Load data from CSV or Excel file."""
    try:
        if file_path.endswith('.csv'):
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            # If all encodings fail, raise error
            raise ValueError(f"Could not decode {file_path} with any common encoding")
        elif file_path.endswith(('.xlsx', '.xls')):
            if sheet_name:
                return pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                return pd.read_excel(file_path)
        else:
            st.error(f"Unsupported file format: {file_path}")
            return None
    except Exception as e:
        st.error(f"Error loading {file_path}: {str(e)}")
        return None

def clean_guest_list(df):
    """
    Clean and dedupe guest list data to prevent double counting.
    Removes summary rows, empty rows, and ensures event columns contain only 0 or 1.
    """
    if df.empty:
        return df
    
    # Create a copy to avoid modifying the original
    cleaned_df = df.copy()
    
    # Remove rows with NaN names (empty rows)
    cleaned_df = cleaned_df.dropna(subset=['Name'])
    
    # Remove summary/header rows by checking if Name contains known summary keywords
    # Using specific keywords to avoid accidentally filtering legitimate guest names
    summary_keywords = ['EVENT SUMMARY', 'CATEGORY BREAKDOWN']
    cleaned_df = cleaned_df[~cleaned_df['Name'].isin(summary_keywords)]
    
    # Remove rows where event columns contain non-binary values
    # Check if event columns exist
    event_cols = ['Engagement Party', 'Maryland Celebration', 'Wedding']
    available_event_cols = [col for col in event_cols if col in cleaned_df.columns]
    
    if available_event_cols:
        # Create a combined mask for all event columns to filter efficiently
        mask = pd.Series([True] * len(cleaned_df), index=cleaned_df.index)
        
        for col in available_event_cols:
            # Convert to string for comparison
            col_str = cleaned_df[col].astype(str)
            # Keep only rows where the value is '0', '1', '0.0', '1.0', or 'nan'
            valid_values = ['0', '1', '0.0', '1.0', 'nan']
            mask &= col_str.isin(valid_values)
        
        cleaned_df = cleaned_df[mask]
    
    # Remove any duplicate guest names (keep first occurrence)
    if 'Name' in cleaned_df.columns:
        cleaned_df = cleaned_df.drop_duplicates(subset=['Name'], keep='first')
    
    # Reset index after filtering
    cleaned_df = cleaned_df.reset_index(drop=True)
    
    return cleaned_df

@st.cache_data
def load_wedding_data(guest_file=None, england_scotland_file=None, france_file=None):
    """Load wedding data from CSV or Excel files."""
    
    # Use provided files or defaults
    guest_path = guest_file or DEFAULT_GUEST_FILE
    england_scotland_path = england_scotland_file or DEFAULT_ENGLAND_SCOTLAND_FILE
    france_path = france_file or DEFAULT_FRANCE_FILE
    
    # Load guest list
    master_list = load_csv_or_excel(guest_path)
    if master_list is None:
        st.error("Failed to load guest list. Using empty dataframe.")
        master_list = pd.DataFrame()
    
    # Clean guest list to prevent double counting
    master_list = clean_guest_list(master_list)
    
    # Load venue data
    england_venues = load_csv_or_excel(england_scotland_path)
    france_venues = load_csv_or_excel(france_path)
    
    if england_venues is None:
        england_venues = pd.DataFrame()
    if france_venues is None:
        france_venues = pd.DataFrame()
    
    # Clean up venue data
    if not england_venues.empty and 'Region/Country' in england_venues.columns:
        england_venues['Country'] = england_venues['Region/Country'].apply(lambda x: 'England' if 'England' in str(x) else 'Scotland')
    elif not england_venues.empty:
        england_venues['Country'] = 'England'
    
    if not france_venues.empty:
        france_venues['Country'] = 'France'
    
    # Combine venue data
    all_venues = pd.concat([england_venues, france_venues], ignore_index=True) if not england_venues.empty or not france_venues.empty else pd.DataFrame()
    
    if not all_venues.empty:
        # Clean Venue column: strip whitespace and handle NaN
        if 'Venue' in all_venues.columns:
            # Fill NaN with empty string, then strip whitespace
            all_venues['Venue'] = all_venues['Venue'].fillna('').astype(str).str.strip()
            # Remove rows with empty venue names
            all_venues = all_venues[all_venues['Venue'] != '']
        # Clean capacity columns - extract numeric values
        def extract_capacity(val):
            if pd.isna(val):
                return None
            val = str(val)
            # Extract first number found
            numbers = re.findall(r'\d+', val)
            return int(numbers[0]) if numbers else None
        
        # Handle different column names
        if 'Seated Dinner Capacity' in all_venues.columns:
            all_venues['Seated Capacity'] = all_venues['Seated Dinner Capacity'].apply(extract_capacity)
        elif 'Seated Capacity' not in all_venues.columns:
            all_venues['Seated Capacity'] = None
            
        if 'Evening/Reception Capacity' in all_venues.columns:
            all_venues['Reception Capacity'] = all_venues['Evening/Reception Capacity'].apply(extract_capacity)
        elif 'Reception Capacity' not in all_venues.columns:
            all_venues['Reception Capacity'] = None
        
        # Parse pricing data from CSV columns if structured columns don't exist
        if 'Base Price (£)' not in all_venues.columns or 'Price per Guest (£)' not in all_venues.columns:
            def parse_venue_pricing(row):
                """Extract base price and per-guest pricing from venue data.
                
                This function parses pricing information from the CSV columns:
                - For England/Scotland: 'Published Venue Hire / Package (GBP)' and 'Per_Head/Menu From (GBP)'
                - For France: 'Published Pricing'
                
                Returns tuple: (base_price, per_guest_price)
                """
                base_price = None
                per_guest = None
                
                # Try to extract per-guest pricing from dedicated Per_Head column FIRST
                # This takes priority over parsing from the venue hire column
                if 'Per_Head/Menu From (GBP)' in row.index and pd.notna(row.get('Per_Head/Menu From (GBP)')):
                    per_head_text = str(row['Per_Head/Menu From (GBP)'])
                    # Look for "From" pricing first - this is usually the starting/minimum price
                    from_match = re.search(r'(?:From|from)\s*£?\s*(\d+(?:,\d{3})*)', per_head_text)
                    if from_match:
                        from_price = int(from_match.group(1).replace(',', ''))
                        if 50 <= from_price <= 1000:
                            per_guest = from_price
                    
                    # If no "From" pricing found, extract all amounts
                    if per_guest is None:
                        amounts = re.findall(r'£?\s*(\d+(?:,\d{3})*)', per_head_text)
                        if amounts:
                            # Clean and convert to numbers
                            clean_amounts = [int(amt.replace(',', '')) for amt in amounts]
                            # Filter for reasonable per-person amounts (£50-£1000)
                            per_person_amounts = [amt for amt in clean_amounts if 50 <= amt <= 1000]
                            if per_person_amounts:
                                per_guest = min(per_person_amounts)
                
                # Try to extract from England/Scotland Published Venue Hire column
                if 'Published Venue Hire / Package (GBP)' in row.index and pd.notna(row.get('Published Venue Hire / Package (GBP)')):
                    venue_hire_text = str(row['Published Venue Hire / Package (GBP)'])
                    
                    # Only extract per-person pricing from here if we didn't get it from Per_Head column
                    if per_guest is None:
                        # Find explicit per-person pricing in this field (marked with "pp")
                        pp_match = re.findall(r'£?\s*(\d+(?:,\d{3})*)\s*(?:pp|per\s*person|per\s*head)', venue_hire_text, re.IGNORECASE)
                        if pp_match:
                            clean_pp = [int(amt.replace(',', '')) for amt in pp_match]
                            # Filter for reasonable per-person amounts
                            per_person_pp = [amt for amt in clean_pp if 50 <= amt <= 1000]
                            if per_person_pp:
                                per_guest = min(per_person_pp)
                    
                    # Extract base venue hire (larger amounts, not marked as "pp")
                    # Split by "packages" to separate venue hire from per-person packages
                    hire_portion = re.split(r'\s*;\s*packages', venue_hire_text, flags=re.IGNORECASE)[0]
                    
                    # Look for currency amounts in the hire portion (typically 4-5 digits for venue hire)
                    # Note: Replace Cyrillic 'У' with '-' as it appears in some CSV data as a range separator
                    amounts = re.findall(r'£?\s*(\d+(?:,\d{3})*)', hire_portion.replace('У', '-'))
                    if amounts:
                        # Clean and convert to numbers
                        clean_amounts = [int(amt.replace(',', '')) for amt in amounts]
                        # Filter for amounts likely to be venue hire (> £1000)
                        venue_hire_amounts = [amt for amt in clean_amounts if amt >= 1000]
                        if venue_hire_amounts:
                            base_price = min(venue_hire_amounts)
                
                # Try to extract from France format
                if 'Published Pricing' in row.index and pd.notna(row.get('Published Pricing')):
                    pricing_text = str(row['Published Pricing'])
                    # Look for Euro amounts and convert to GBP (approximate 1 EUR = 0.85 GBP as of 2025)
                    euro_amounts = re.findall(r'€\s*(\d+(?:,\d{3})*)', pricing_text)
                    if euro_amounts:
                        clean_amounts = [int(amt.replace(',', '')) for amt in euro_amounts]
                        # Convert EUR to GBP (0.85 conversion rate)
                        if base_price is None and clean_amounts:
                            base_price = int(min(clean_amounts) * 0.85)
                    
                    # Also check for per person pricing in euros
                    # Match patterns like "€125–€180 pp" or "Menu €125"
                    per_person_match = re.search(r'(?:Menu|pp)\s*€?\s*(\d+)', pricing_text, re.IGNORECASE)
                    if per_person_match and per_guest is None:
                        per_guest = int(int(per_person_match.group(1)) * 0.85)
                
                # Apply venue-specific documented pricing where available (2025 rates from web research)
                # These override parsed values when web research indicates more accurate current pricing
                venue_name = str(row.get('Venue', '')).lower()
                
                # Research-based pricing adjustments for key venues (2025 data)
                if 'ashridge house' in venue_name:
                    # Web research 2025: £20,000-£35,000 packages, ~£224 per person
                    if base_price is None or base_price < 15000:
                        base_price = 20000  # Starting from £20,000 for 2025
                    # Keep parsed £229 per guest as it matches research
                        
                elif 'cliveden house' in venue_name:
                    # Web research 2025: Exclusive use £36,000-£72,000, packages £330-£510 pp
                    if base_price is None:
                        base_price = 45600  # Midweek exclusive use starts ~£45,600
                    # Override low private dining price with package pricing
                    if per_guest is not None and per_guest < 200:
                        per_guest = 330  # Package prices from £330 per person (2025 research)
                        
                elif 'château de berne' in venue_name or 'chateau de berne' in venue_name:
                    # Web research 2025: €4,800 venue hire, €150-€350 per person
                    if base_price is None:
                        base_price = int(4800 * 0.85)  # €4,800 = ~£4,080
                    if per_guest is None:
                        per_guest = int(150 * 0.85)  # From €150 per person = ~£128
                
                # Default estimates based on venue style and capacity for missing data
                # Only use estimates when no pricing data is available at all
                if base_price is None or per_guest is None:
                    country = str(row.get('Country', '')).lower()
                    seated_capacity = row.get('Seated Capacity', 150)
                    
                    # Realistic baseline estimates by country and capacity tier (2025 UK wedding market)
                    if country == 'england' or country == 'scotland':
                        if seated_capacity and seated_capacity >= 200:
                            if base_price is None:
                                base_price = 35000  # Larger stately homes/castles
                            if per_guest is None:
                                per_guest = 180
                        elif seated_capacity and seated_capacity >= 100:
                            if base_price is None:
                                base_price = 18000  # Mid-tier country houses
                            if per_guest is None:
                                per_guest = 160
                        else:
                            if base_price is None:
                                base_price = 12000  # Smaller intimate venues
                            if per_guest is None:
                                per_guest = 140
                    elif country == 'france':
                        # French châteaux pricing in GBP equivalent
                        if seated_capacity and seated_capacity >= 150:
                            if base_price is None:
                                base_price = 25000
                            if per_guest is None:
                                per_guest = 150
                        else:
                            if base_price is None:
                                base_price = 15000
                            if per_guest is None:
                                per_guest = 130
                    else:
                        # Generic fallback
                        if base_price is None:
                            base_price = 20000
                        if per_guest is None:
                            per_guest = 150
                
                return base_price, per_guest
            
            # Apply pricing extraction to all venues
            pricing_data = all_venues.apply(parse_venue_pricing, axis=1)
            
            if 'Base Price (£)' not in all_venues.columns:
                all_venues['Base Price (£)'] = pricing_data.apply(lambda x: x[0])
            if 'Price per Guest (£)' not in all_venues.columns:
                all_venues['Price per Guest (£)'] = pricing_data.apply(lambda x: x[1])
    
    # Process master list
    if not master_list.empty and all(col in master_list.columns for col in ['Engagement Party', 'Maryland Celebration', 'Wedding']):
        # Ensure event columns are numeric
        for col in ['Engagement Party', 'Maryland Celebration', 'Wedding']:
            master_list[col] = pd.to_numeric(master_list[col], errors='coerce').fillna(0).astype(int)
        master_list['Total Events'] = master_list[['Engagement Party', 'Maryland Celebration', 'Wedding']].sum(axis=1)
    elif not master_list.empty and 'Total Events' not in master_list.columns:
        master_list['Total Events'] = 0
    
    return master_list, all_venues, england_venues, france_venues

# Initialize session state for uploaded files
if 'guest_file_path' not in st.session_state:
    st.session_state.guest_file_path = None
if 'england_scotland_file_path' not in st.session_state:
    st.session_state.england_scotland_file_path = None
if 'france_file_path' not in st.session_state:
    st.session_state.france_file_path = None

# Load data with session state paths
guest_list, all_venues, england_venues, france_venues = load_wedding_data(
    st.session_state.guest_file_path,
    st.session_state.england_scotland_file_path,
    st.session_state.france_file_path
)

# Initialize session state for table arrangements
if 'table_assignments' not in st.session_state:
    st.session_state.table_assignments = {}
if 'table_config' not in st.session_state:
    st.session_state.table_config = {
        'num_tables': 20,
        'seats_per_table': 10
    }

# Main Title
st.title("💍 Wedding Planning Dashboard")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    
    # File upload section
    st.subheader("📂 Data Files")
    
    with st.expander("Upload CSV Files", expanded=False):
        st.markdown("Upload your own CSV files to replace the default data.")
        
        # Guest list upload
        guest_upload = st.file_uploader(
            "Guest List CSV",
            type=['csv'],
            key='guest_uploader',
            help="CSV file with columns: Name, Engagement Party, Maryland Celebration, Wedding, Category, Source"
        )
        
        if guest_upload is not None:
            # Validate file size (Streamlit already enforces 200MB limit)
            file_size = guest_upload.size
            if file_size > 200 * 1024 * 1024:  # 200MB
                st.error("File too large. Maximum size is 200MB.")
            else:
                try:
                    # Save uploaded file with sanitized name
                    guest_file_path = os.path.join(DATA_DIR, 'uploaded_guest_list.csv')
                    with open(guest_file_path, 'wb') as f:
                        f.write(guest_upload.getbuffer())
                    st.session_state.guest_file_path = guest_file_path
                    st.success("✓ Guest list uploaded!")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error uploading file: {str(e)}")
        
        # England/Scotland venues upload
        england_upload = st.file_uploader(
            "England/Scotland Venues CSV",
            type=['csv'],
            key='england_uploader',
            help="CSV file with venue information for England and Scotland"
        )
        
        if england_upload is not None:
            try:
                # Save uploaded file with sanitized name
                england_file_path = os.path.join(DATA_DIR, 'uploaded_england_scotland.csv')
                with open(england_file_path, 'wb') as f:
                    f.write(england_upload.getbuffer())
                st.session_state.england_scotland_file_path = england_file_path
                st.success("✓ England/Scotland venues uploaded!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error uploading file: {str(e)}")
        
        # France venues upload
        france_upload = st.file_uploader(
            "France Venues CSV",
            type=['csv'],
            key='france_uploader',
            help="CSV file with venue information for France"
        )
        
        if france_upload is not None:
            try:
                # Save uploaded file with sanitized name
                france_file_path = os.path.join(DATA_DIR, 'uploaded_france.csv')
                with open(france_file_path, 'wb') as f:
                    f.write(france_upload.getbuffer())
                st.session_state.france_file_path = france_file_path
                st.success("✓ France venues uploaded!")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error uploading file: {str(e)}")
            st.cache_data.clear()
            st.rerun()
        
        # Reset to defaults
        if st.button("🔄 Reset to Default Files"):
            st.session_state.guest_file_path = None
            st.session_state.england_scotland_file_path = None
            st.session_state.france_file_path = None
            st.cache_data.clear()
            st.rerun()
        
        # Show current data source
        st.markdown("**Current Data Sources:**")
        st.markdown(f"- Guest List: `{st.session_state.guest_file_path or DEFAULT_GUEST_FILE}`")
        st.markdown(f"- England/Scotland: `{st.session_state.england_scotland_file_path or DEFAULT_ENGLAND_SCOTLAND_FILE}`")
        st.markdown(f"- France: `{st.session_state.france_file_path or DEFAULT_FRANCE_FILE}`")
    
    st.markdown("---")
    
    # Guest count filter
    st.subheader("Guest Filters")
    event_filter = st.selectbox(
        "Filter by Event",
        ["All Events", "Wedding", "Engagement Party", "Maryland Celebration"]
    )
    
    if not guest_list.empty and 'Category' in guest_list.columns:
        category_filter = st.multiselect(
            "Filter by Category",
            options=guest_list['Category'].unique().tolist(),
            default=guest_list['Category'].unique().tolist()
        )
    else:
        category_filter = []
    
    st.markdown("---")
    
    # Venue filters
    st.subheader("Venue Filters")
    
    if not all_venues.empty and 'Country' in all_venues.columns:
        available_countries = all_venues['Country'].unique().tolist()
        country_filter = st.multiselect(
            "Select Countries",
            options=available_countries,
            default=available_countries
        )
    else:
        country_filter = []
    
    capacity_range = st.slider(
        "Seated Capacity Range",
        min_value=0,
        max_value=300,
        value=(100, 200)
    )
    
    price_range = st.slider(
        "Base Price Range (£)",
        min_value=0,
        max_value=100000,
        value=(10000, 80000),
        step=5000
    )

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Venue Comparison", "👥 Guest Management", "🪑 Table Seating", "📈 Analytics"])

# Tab 1: Venue Comparison
with tab1:
    st.header("Venue Comparison & Analysis")
    
    if all_venues.empty:
        st.warning("⚠️ No venue data loaded. Please upload venue CSV files using the sidebar.")
        st.info(
            "Expected CSV format:\n\n"
            "- **Venue**: Name of the venue\n"
            "- **Region/Country**: Location information\n"
            "- **Style**: Venue style/type\n"
            "- **Seated Dinner Capacity**: Capacity for seated dinner\n"
            "- **Evening/Reception Capacity**: Capacity for reception\n"
            "- **Exclusive Use?**: Whether exclusive use is available\n"
            "- **Bedrooms Onsite**: Number of bedrooms\n"
            "- **Nearest Airports**: Nearby airports\n\n"
            "You can also add columns like 'Base Price (£)' and 'Price per Guest (£)' for pricing information."
        )
    else:
        # Filter venues
        filtered_venues = all_venues[all_venues['Country'].isin(country_filter)].copy()
        
        if 'Seated Capacity' in filtered_venues.columns:
            filtered_venues = filtered_venues[
                (filtered_venues['Seated Capacity'].between(capacity_range[0], capacity_range[1], inclusive='both')) |
                (filtered_venues['Seated Capacity'].isna())
            ]
        
        if 'Base Price (£)' in filtered_venues.columns:
            filtered_venues = filtered_venues[
                filtered_venues['Base Price (£)'].between(price_range[0], price_range[1])
            ]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Venues", len(filtered_venues))
        with col2:
            if 'Base Price (£)' in filtered_venues.columns:
                avg_price = filtered_venues['Base Price (£)'].mean()
                st.metric("Average Base Price", f"£{avg_price:,.0f}" if not pd.isna(avg_price) else "N/A")
            else:
                st.metric("Average Base Price", "N/A")
        with col3:
            if 'Seated Capacity' in filtered_venues.columns:
                avg_capacity = filtered_venues['Seated Capacity'].mean()
                st.metric("Avg Seated Capacity", f"{avg_capacity:.0f}" if not pd.isna(avg_capacity) else "N/A")
            else:
                st.metric("Avg Seated Capacity", "N/A")
        
        st.markdown("---")
        
        # Venue comparison chart
        col1, col2 = st.columns(2)
        
        with col1:
            # Price vs Capacity scatter plot
            if not filtered_venues.empty and 'Seated Capacity' in filtered_venues.columns and 'Base Price (£)' in filtered_venues.columns:
                hover_cols = ['Venue', 'Style', 'Exclusive Use?']
                hover_data = {col: True for col in hover_cols if col in filtered_venues.columns}
                
                fig_scatter = px.scatter(
                    filtered_venues,
                    x='Seated Capacity',
                    y='Base Price (£)',
                    color='Country',
                    size='Price per Guest (£)' if 'Price per Guest (£)' in filtered_venues.columns else None,
                    hover_data=hover_data,
                    title='Price vs Capacity Analysis',
                    labels={'Base Price (£)': 'Base Price (£)', 'Seated Capacity': 'Seated Capacity'}
                )
                fig_scatter.update_layout(height=400)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Add 'Seated Capacity' and 'Base Price (£)' columns to your data for price vs capacity analysis.")
        
        with col2:
            # Price distribution by country
            if not filtered_venues.empty and 'Base Price (£)' in filtered_venues.columns:
                fig_box = px.box(
                    filtered_venues,
                    x='Country',
                    y='Base Price (£)',
                    color='Country',
                    title='Price Distribution by Country'
                )
                fig_box.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("Add 'Base Price (£)' column to your data for price distribution analysis.")
        
        # Detailed venue table
        st.subheader("Detailed Venue Information")
        
        # Prepare display columns
        display_cols = ['Venue', 'Country', 'Style', 'Seated Capacity', 
                       'Base Price (£)', 'Price per Guest (£)', 'Exclusive Use?', 
                       'Bedrooms Onsite', 'Nearest Airports']
        
        # Filter to only columns that exist
        display_cols = [col for col in display_cols if col in filtered_venues.columns]
        
        venue_display = filtered_venues[display_cols].copy()
        
        # Format price columns if they exist
        if 'Base Price (£)' in venue_display.columns:
            venue_display['Base Price (£)'] = venue_display['Base Price (£)'].apply(lambda x: f"£{x:,.0f}" if pd.notna(x) else "N/A")
        if 'Price per Guest (£)' in venue_display.columns:
            venue_display['Price per Guest (£)'] = venue_display['Price per Guest (£)'].apply(lambda x: f"£{x:.0f}" if pd.notna(x) else "N/A")
        
        st.dataframe(
            venue_display,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Download venue data
        st.markdown("---")
        st.subheader("💾 Export Venue Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download filtered venues
            filtered_csv = filtered_venues.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Venues",
                data=filtered_csv,
                file_name=f"filtered_venues_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                help="Download currently filtered venues"
            )
        
        with col2:
            # Download England/Scotland venues
            if not england_venues.empty:
                england_csv = england_venues.to_csv(index=False)
                st.download_button(
                    label="📥 England/Scotland Venues",
                    data=england_csv,
                    file_name="englandscotland_csv.csv",
                    mime='text/csv',
                    help="Download to replace englandscotland_csv.csv in repo"
                )
        
        with col3:
            # Download France venues
            if not france_venues.empty:
                france_csv = france_venues.to_csv(index=False)
                st.download_button(
                    label="📥 France Venues",
                    data=france_csv,
                    file_name="france_csv.csv",
                    mime='text/csv',
                    help="Download to replace france_csv.csv in repo"
                )
        
        st.info(
            "💡 **Tip:** To permanently update venue data:\n"
            "1. Click the respective download button\n"
            "2. Replace the corresponding CSV file in your local repo\n"
            "3. Commit and push the changes to GitHub"
        )
        
        # Venue cost calculator
        st.markdown("---")
        st.subheader("💰 Venue Cost Calculator")
        
        # Use all_venues for dropdown (unfiltered), not filtered_venues
        if not all_venues.empty and 'Venue' in all_venues.columns:
            # Get unique venue names from all venues (already cleaned in load_wedding_data)
            all_venue_names = all_venues['Venue'].unique().tolist()
            
            # Show warning if filters are hiding venues from analysis
            num_filtered = len(filtered_venues) if not filtered_venues.empty else 0
            if num_filtered < len(all_venues):
                st.info(f"ℹ️ Showing {num_filtered} of {len(all_venues)} venues in analysis above. Adjust filters to see more. All venues available in calculator below.")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_venue = st.selectbox(
                    "Select Venue",
                    options=all_venue_names
                )
            
            with col2:
                guest_count = st.number_input(
                    "Number of Guests",
                    min_value=1,
                    max_value=300,
                    value=150
                )
            
            # Look up venue data from all_venues (not filtered)
            if selected_venue and 'Base Price (£)' in all_venues.columns and 'Price per Guest (£)' in all_venues.columns:
                venue_matches = all_venues[all_venues['Venue'] == selected_venue]
                if not venue_matches.empty:
                    venue_data = venue_matches.iloc[0]
                    base_price = venue_data['Base Price (£)']
                    per_guest = venue_data['Price per Guest (£)']
                    total_cost = base_price + (guest_count * per_guest)
                    
                    with col3:
                        st.metric("Estimated Total Cost", f"£{total_cost:,.0f}")
                    
                    # Cost breakdown
                    st.markdown("**Cost Breakdown:**")
                    breakdown_df = pd.DataFrame({
                        'Item': ['Base Venue Fee', 'Per Guest Cost', 'Total'],
                        'Cost': [f"£{base_price:,.0f}", 
                                f"£{guest_count * per_guest:,.0f} ({guest_count} × £{per_guest:.0f})",
                                f"£{total_cost:,.0f}"]
                    })
                    st.table(breakdown_df)
                else:
                    st.warning("⚠️ Selected venue not found in data.")
            elif selected_venue:
                st.info("Add 'Base Price (£)' and 'Price per Guest (£)' columns to your venue data for cost calculations.")
        else:
            st.info("Upload venue data to use the cost calculator.")

# Tab 2: Guest Management
with tab2:
    st.header("Guest List Management")
    
    if guest_list.empty:
        st.warning("⚠️ No guest data loaded. Please upload a guest list CSV using the sidebar.")
        st.info(
            "Expected CSV format:\n\n"
            "- **Name**: Guest name\n"
            "- **Engagement Party**: 1 or 0 (attending or not)\n"
            "- **Maryland Celebration**: 1 or 0 (attending or not)\n"
            "- **Wedding**: 1 or 0 (attending or not)\n"
            "- **Category**: Guest category (e.g., Family, Friends)\n"
            "- **Source**: Source of invitation (e.g., John B, Darling)\n\n"
            "Optional:\n"
            "- **Total Events**: Will be calculated automatically if not provided"
        )
    else:
        # Apply filters
        filtered_guests = guest_list.copy()
        
        if 'Category' in guest_list.columns and category_filter:
            filtered_guests = filtered_guests[filtered_guests['Category'].isin(category_filter)]
        
        if event_filter != "All Events" and event_filter in filtered_guests.columns:
            filtered_guests = filtered_guests[filtered_guests[event_filter] == 1]
        
        # Guest metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_guests = len(filtered_guests)
            st.metric("Total Guests", total_guests)
        
        with col2:
            wedding_count = filtered_guests['Wedding'].sum() if 'Wedding' in filtered_guests.columns else 0
            st.metric("Wedding Attendees", int(wedding_count))
        
        with col3:
            engagement_count = filtered_guests['Engagement Party'].sum() if 'Engagement Party' in filtered_guests.columns else 0
            st.metric("Engagement Party", int(engagement_count))
        
        with col4:
            maryland_count = filtered_guests['Maryland Celebration'].sum() if 'Maryland Celebration' in filtered_guests.columns else 0
            st.metric("Maryland Celebration", int(maryland_count))
        
        st.markdown("---")
        
        # Guest breakdown charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Category breakdown
            if 'Category' in filtered_guests.columns:
                category_counts = filtered_guests['Category'].value_counts()
                fig_pie = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title='Guest Distribution by Category'
                )
                fig_pie.update_layout(height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Add 'Category' column to your guest data for category analysis.")
        
        with col2:
            # Event attendance
            event_cols = ['Wedding', 'Engagement Party', 'Maryland Celebration']
            available_events = [col for col in event_cols if col in filtered_guests.columns]
            
            if available_events:
                event_data = pd.DataFrame({
                    'Event': available_events,
                    'Attendees': [filtered_guests[col].sum() for col in available_events]
                })
                fig_bar = px.bar(
                    event_data,
                    x='Event',
                    y='Attendees',
                    title='Attendance by Event',
                    color='Event'
                )
                fig_bar.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Add event columns (Wedding, Engagement Party, Maryland Celebration) for attendance analysis.")
        
        # Guest list table
        st.subheader("Guest List Details")
        
        # Add search functionality
        search_term = st.text_input("🔍 Search guests by name", "")
        
        if search_term and 'Name' in filtered_guests.columns:
            filtered_guests = filtered_guests[
                filtered_guests['Name'].str.contains(search_term, case=False, na=False)
            ]
        
        # Display guest list
        base_cols = ['Name', 'Category', 'Source']
        event_cols = ['Engagement Party', 'Maryland Celebration', 'Wedding', 'Total Events']
        
        display_cols = [col for col in base_cols + event_cols if col in filtered_guests.columns]
        guest_display = filtered_guests[display_cols].copy()
        
        # Convert 1/0 to Yes/No for events
        for col in ['Engagement Party', 'Maryland Celebration', 'Wedding']:
            if col in guest_display.columns:
                guest_display[col] = guest_display[col].apply(lambda x: '✓' if x == 1 else '')
        
        st.dataframe(
            guest_display,
            use_container_width=True,
            height=400,
            hide_index=True
        )
        
        # Download guest list
        st.markdown("---")
        st.subheader("💾 Export & Update Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = filtered_guests.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Guest List (CSV)",
                data=csv,
                file_name=f"guest_list_{datetime.now().strftime('%Y%m%d')}.csv",
                mime='text/csv',
                help="Download the currently filtered guest list"
            )
        
        with col2:
            # Download full guest list for updating repo
            full_csv = guest_list.to_csv(index=False)
            st.download_button(
                label="📥 Download Full Guest List (CSV)",
                data=full_csv,
                file_name="wedding_roster_csv.csv",
                mime='text/csv',
                help="Download the complete guest list to replace wedding_roster_csv.csv in the repo"
            )
        
        st.info(
            "💡 **Tip:** To permanently update the guest list:\n"
            "1. Click 'Download Full Guest List'\n"
            "2. Replace the `wedding_roster_csv.csv` file in your local repo\n"
            "3. Commit and push the changes to GitHub\n\n"
            "Or use the file uploader above to test changes in this session."
        )

# Tab 3: Table Seating
with tab3:
    st.header("Table Seating Arrangement")
    
    # Get wedding guests only
    wedding_guests = guest_list[guest_list['Wedding'] == 1].copy()
    total_wedding_guests = len(wedding_guests)
    
    # Table configuration
    st.subheader("⚙️ Table Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_tables = st.number_input(
            "Number of Tables",
            min_value=1,
            max_value=50,
            value=st.session_state.table_config['num_tables']
        )
        st.session_state.table_config['num_tables'] = num_tables
    
    with col2:
        seats_per_table = st.number_input(
            "Seats per Table",
            min_value=1,
            max_value=20,
            value=st.session_state.table_config['seats_per_table']
        )
        st.session_state.table_config['seats_per_table'] = seats_per_table
    
    with col3:
        total_capacity = num_tables * seats_per_table
        st.metric("Total Capacity", total_capacity)
        if total_wedding_guests > total_capacity:
            st.error(f"⚠️ Need {total_wedding_guests - total_capacity} more seats!")
        else:
            st.success(f"✓ {total_capacity - total_wedding_guests} spare seats")
    
    st.markdown("---")
    
    # Table assignment interface
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Guest Assignment")
        
        # Initialize assignments if needed
        if not st.session_state.table_assignments:
            # Auto-assign guests to tables
            for i, guest in enumerate(wedding_guests['Name'].tolist()):
                table_num = (i % num_tables) + 1
                st.session_state.table_assignments[guest] = table_num
        
        # Manual assignment
        selected_guest = st.selectbox(
            "Select Guest",
            options=wedding_guests['Name'].tolist()
        )
        
        if selected_guest:
            current_table = st.session_state.table_assignments.get(selected_guest, 1)
            new_table = st.number_input(
                f"Assign {selected_guest} to Table",
                min_value=1,
                max_value=num_tables,
                value=current_table
            )
            st.session_state.table_assignments[selected_guest] = new_table
            
            # Show guest details
            guest_info = wedding_guests[wedding_guests['Name'] == selected_guest].iloc[0]
            st.info(f"**Category:** {guest_info['Category']}")
            st.info(f"**Source:** {guest_info['Source']}")
        
        # Auto-arrange options
        st.markdown("---")
        st.subheader("Auto-Arrange Options")
        
        if st.button("🔄 Random Shuffle"):
            guests = wedding_guests['Name'].tolist()
            random.shuffle(guests)
            for i, guest in enumerate(guests):
                table_num = (i % num_tables) + 1
                st.session_state.table_assignments[guest] = table_num
            st.rerun()
        
        if st.button("👥 Group by Category"):
            # Group guests by category
            for category in wedding_guests['Category'].unique():
                cat_guests = wedding_guests[wedding_guests['Category'] == category]['Name'].tolist()
                start_table = hash(category) % num_tables
                for i, guest in enumerate(cat_guests):
                    table_num = ((start_table + i // seats_per_table) % num_tables) + 1
                    st.session_state.table_assignments[guest] = table_num
            st.rerun()
    
    with col2:
        st.subheader("Table Layout Visualization")
        
        # Create table visualization
        table_data = {}
        for guest, table in st.session_state.table_assignments.items():
            if table not in table_data:
                table_data[table] = []
            table_data[table].append(guest)
        
        # Display tables in a grid
        cols_per_row = 4
        for row in range(0, num_tables, cols_per_row):
            cols = st.columns(cols_per_row)
            for i, col in enumerate(cols):
                table_num = row + i + 1
                if table_num <= num_tables:
                    with col:
                        guests_at_table = table_data.get(table_num, [])
                        occupancy = len(guests_at_table)
                        
                        # Color code based on occupancy
                        if occupancy == 0:
                            color = "🔴"
                        elif occupancy < seats_per_table:
                            color = "🟡"
                        else:
                            color = "🟢"
                        
                        st.markdown(f"### {color} Table {table_num}")
                        st.markdown(f"**{occupancy}/{seats_per_table} seats**")
                        
                        if guests_at_table:
                            for guest in guests_at_table[:seats_per_table]:
                                st.markdown(f"• {guest}")
                            if len(guests_at_table) > seats_per_table:
                                st.warning(f"⚠️ {len(guests_at_table) - seats_per_table} overflow!")
                        else:
                            st.markdown("*Empty*")
    
    # Export seating chart
    st.markdown("---")
    st.subheader("📄 Export Seating Chart")
    
    # Create seating chart dataframe
    seating_chart = []
    for guest, table in st.session_state.table_assignments.items():
        guest_info = wedding_guests[wedding_guests['Name'] == guest].iloc[0] if guest in wedding_guests['Name'].values else None
        if guest_info is not None:
            seating_chart.append({
                'Table': table,
                'Guest Name': guest,
                'Category': guest_info['Category'],
                'Source': guest_info['Source']
            })
    
    seating_df = pd.DataFrame(seating_chart)
    seating_df = seating_df.sort_values(['Table', 'Guest Name'])
    
    # Download button
    csv_seating = seating_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Seating Chart (CSV)",
        data=csv_seating,
        file_name=f"seating_chart_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
    )

# Tab 4: Analytics
with tab4:
    st.header("Wedding Analytics & Insights")
    
    # Overall statistics
    st.subheader("📊 Overall Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_events = guest_list['Total Events'].mean()
        st.metric("Avg Events/Guest", f"{avg_events:.1f}")
    
    with col2:
        overlap_all = len(guest_list[(guest_list['Wedding'] == 1) & 
                                     (guest_list['Engagement Party'] == 1) & 
                                     (guest_list['Maryland Celebration'] == 1)])
        st.metric("Attending All Events", overlap_all)
    
    with col3:
        wedding_only = len(guest_list[(guest_list['Wedding'] == 1) & 
                                      (guest_list['Total Events'] == 1)])
        st.metric("Wedding Only", wedding_only)
    
    with col4:
        multi_event = len(guest_list[guest_list['Total Events'] > 1])
        st.metric("Multi-Event Guests", multi_event)
    
    st.markdown("---")
    
    # Event overlap analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Venn diagram simulation with bar chart
        overlap_data = {
            'Wedding Only': wedding_only,
            'All Three Events': overlap_all,
            'Wedding + Engagement': len(guest_list[(guest_list['Wedding'] == 1) & 
                                                   (guest_list['Engagement Party'] == 1) & 
                                                   (guest_list['Maryland Celebration'] == 0)]),
            'Wedding + Maryland': len(guest_list[(guest_list['Wedding'] == 1) & 
                                                 (guest_list['Maryland Celebration'] == 1) & 
                                                 (guest_list['Engagement Party'] == 0)])
        }
        
        fig_overlap = px.bar(
            x=list(overlap_data.keys()),
            y=list(overlap_data.values()),
            title='Event Attendance Overlap',
            labels={'x': 'Attendance Pattern', 'y': 'Number of Guests'}
        )
        fig_overlap.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_overlap, use_container_width=True)
    
    with col2:
        # Source analysis
        source_stats = guest_list.groupby('Source').agg({
            'Name': 'count',
            'Wedding': 'sum',
            'Engagement Party': 'sum',
            'Maryland Celebration': 'sum'
        }).rename(columns={'Name': 'Total Invited'})
        
        source_stats = source_stats.reset_index()
        fig_source = px.bar(
            source_stats,
            x='Source',
            y=['Wedding', 'Engagement Party', 'Maryland Celebration'],
            title='Guest Source Analysis',
            labels={'value': 'Number of Guests', 'variable': 'Event'}
        )
        fig_source.update_layout(height=400)
        st.plotly_chart(fig_source, use_container_width=True)
    
    # Category deep dive
    st.markdown("---")
    st.subheader("📈 Category Analysis")
    
    category_stats = guest_list.groupby('Category').agg({
        'Name': 'count',
        'Wedding': 'sum',
        'Engagement Party': 'sum',
        'Maryland Celebration': 'sum',
        'Total Events': 'mean'
    }).round(2)
    
    category_stats.columns = ['Total Guests', 'Wedding', 'Engagement', 'Maryland', 'Avg Events']
    category_stats = category_stats.sort_values('Total Guests', ascending=False)
    
    # Display as styled dataframe
    st.dataframe(
        category_stats,
        use_container_width=True,
        height=300
    )
    
    # Venue country comparison
    st.markdown("---")
    st.subheader("🌍 Venue Country Comparison")
    
    if not all_venues.empty and 'Country' in all_venues.columns:
        required_cols = ['Venue', 'Base Price (£)', 'Seated Capacity', 'Price per Guest (£)']
        available_cols = {col: col for col in required_cols if col in all_venues.columns}
        
        if available_cols:
            agg_dict = {}
            if 'Venue' in available_cols:
                agg_dict['Venue'] = 'count'
            if 'Base Price (£)' in available_cols:
                agg_dict['Base Price (£)'] = ['mean', 'min', 'max']
            if 'Seated Capacity' in available_cols:
                agg_dict['Seated Capacity'] = 'mean'
            if 'Price per Guest (£)' in available_cols:
                agg_dict['Price per Guest (£)'] = 'mean'
            
            country_stats = all_venues.groupby('Country').agg(agg_dict).round(0)
            
            # Flatten column names
            country_stats.columns = ['_'.join(col).strip('_') if isinstance(col, tuple) else col for col in country_stats.columns]
            
            st.dataframe(
                country_stats,
                use_container_width=True
            )
        else:
            st.info("Add venue data columns (Venue, Base Price, etc.) for country comparison.")
    else:
        st.info("Upload venue data with Country information for country comparison.")
    
    # Budget scenarios
    st.markdown("---")
    st.subheader("💰 Budget Scenarios")
    
    if not all_venues.empty and 'Country' in all_venues.columns and 'Base Price (£)' in all_venues.columns and 'Price per Guest (£)' in all_venues.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            scenario_guests = st.slider("Scenario Guest Count", 100, 250, 150, 10)
        
        with col2:
            available_countries = all_venues['Country'].unique().tolist()
            default_countries = [c for c in ['England', 'France'] if c in available_countries]
            selected_countries = st.multiselect(
                "Countries to Compare",
                available_countries,
                default=default_countries if default_countries else available_countries[:2] if len(available_countries) >= 2 else available_countries
            )
        
        if selected_countries:
            scenario_data = []
            for country in selected_countries:
                country_venues = all_venues[all_venues['Country'] == country]
                
                if not country_venues.empty:
                    min_cost = country_venues['Base Price (£)'].min() + (scenario_guests * country_venues['Price per Guest (£)'].min())
                    avg_cost = country_venues['Base Price (£)'].mean() + (scenario_guests * country_venues['Price per Guest (£)'].mean())
                    max_cost = country_venues['Base Price (£)'].max() + (scenario_guests * country_venues['Price per Guest (£)'].max())
                    
                    scenario_data.append({
                        'Country': country,
                        'Minimum': min_cost,
                        'Average': avg_cost,
                        'Maximum': max_cost
                    })
            
            if scenario_data:
                scenario_df = pd.DataFrame(scenario_data)
                
                fig_scenario = px.bar(
                    scenario_df,
                    x='Country',
                    y=['Minimum', 'Average', 'Maximum'],
                    title=f'Cost Scenarios for {scenario_guests} Guests',
                    labels={'value': 'Estimated Cost (£)', 'variable': 'Scenario'},
                    barmode='group'
                )
                fig_scenario.update_layout(height=400)
                st.plotly_chart(fig_scenario, use_container_width=True)
    else:
        st.info("Upload venue data with pricing information (Base Price and Price per Guest) for budget scenarios.")

# Footer
st.markdown("---")
st.markdown("*Wedding Planning Dashboard • Last Updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
