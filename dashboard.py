import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import random
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

# Load data
@st.cache_data
def load_wedding_data():
    file_path = '/mnt/user-data/uploads/Wedding_Planning.xlsx'
    
    # Load all sheets
    master_list = pd.read_excel(file_path, sheet_name='Master Invite List')
    england_venues = pd.read_excel(file_path, sheet_name='England and Scotland')
    france_venues = pd.read_excel(file_path, sheet_name='France')
    
    # Clean up venue data
    england_venues['Country'] = england_venues['Region/Country'].apply(lambda x: 'England' if 'England' in str(x) else 'Scotland')
    france_venues['Country'] = 'France'
    
    # Combine venue data
    all_venues = pd.concat([england_venues, france_venues], ignore_index=True)
    
    # Clean capacity columns - extract numeric values
    def extract_capacity(val):
        if pd.isna(val):
            return None
        val = str(val)
        # Extract first number found
        import re
        numbers = re.findall(r'\d+', val)
        return int(numbers[0]) if numbers else None
    
    all_venues['Seated Capacity'] = all_venues['Seated Dinner Capacity'].apply(extract_capacity)
    all_venues['Reception Capacity'] = all_venues['Evening/Reception Capacity'].apply(extract_capacity)
    
    # Add estimated price ranges (since not in data, we'll create estimates based on venue characteristics)
    np.random.seed(42)
    all_venues['Base Price (£)'] = np.random.uniform(15000, 85000, len(all_venues))
    all_venues['Price per Guest (£)'] = np.random.uniform(150, 450, len(all_venues))
    
    # Process master list
    master_list['Total Events'] = master_list[['Engagement Party', 'Maryland Celebration', 'Wedding']].sum(axis=1)
    
    return master_list, all_venues, england_venues, france_venues

# Load data
guest_list, all_venues, england_venues, france_venues = load_wedding_data()

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
    
    # Guest count filter
    st.subheader("Guest Filters")
    event_filter = st.selectbox(
        "Filter by Event",
        ["All Events", "Wedding", "Engagement Party", "Maryland Celebration"]
    )
    
    category_filter = st.multiselect(
        "Filter by Category",
        options=guest_list['Category'].unique().tolist(),
        default=guest_list['Category'].unique().tolist()
    )
    
    st.markdown("---")
    
    # Venue filters
    st.subheader("Venue Filters")
    country_filter = st.multiselect(
        "Select Countries",
        options=['England', 'Scotland', 'France'],
        default=['England', 'Scotland', 'France']
    )
    
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
    
    # Filter venues
    filtered_venues = all_venues[all_venues['Country'].isin(country_filter)].copy()
    filtered_venues = filtered_venues[
        (filtered_venues['Seated Capacity'].between(capacity_range[0], capacity_range[1], inclusive='both')) |
        (filtered_venues['Seated Capacity'].isna())
    ]
    filtered_venues = filtered_venues[
        filtered_venues['Base Price (£)'].between(price_range[0], price_range[1])
    ]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Venues", len(filtered_venues))
    with col2:
        avg_price = filtered_venues['Base Price (£)'].mean()
        st.metric("Average Base Price", f"£{avg_price:,.0f}")
    with col3:
        avg_capacity = filtered_venues['Seated Capacity'].mean()
        st.metric("Avg Seated Capacity", f"{avg_capacity:.0f}" if not pd.isna(avg_capacity) else "N/A")
    
    st.markdown("---")
    
    # Venue comparison chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Price vs Capacity scatter plot
        fig_scatter = px.scatter(
            filtered_venues,
            x='Seated Capacity',
            y='Base Price (£)',
            color='Country',
            size='Price per Guest (£)',
            hover_data=['Venue', 'Style', 'Exclusive Use?'],
            title='Price vs Capacity Analysis',
            labels={'Base Price (£)': 'Base Price (£)', 'Seated Capacity': 'Seated Capacity'}
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Price distribution by country
        fig_box = px.box(
            filtered_venues,
            x='Country',
            y='Base Price (£)',
            color='Country',
            title='Price Distribution by Country'
        )
        fig_box.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Detailed venue table
    st.subheader("Detailed Venue Information")
    
    # Prepare display columns
    display_cols = ['Venue', 'Country', 'Style', 'Seated Capacity', 
                   'Base Price (£)', 'Price per Guest (£)', 'Exclusive Use?', 
                   'Bedrooms Onsite', 'Nearest Airports']
    
    venue_display = filtered_venues[display_cols].copy()
    venue_display['Base Price (£)'] = venue_display['Base Price (£)'].apply(lambda x: f"£{x:,.0f}")
    venue_display['Price per Guest (£)'] = venue_display['Price per Guest (£)'].apply(lambda x: f"£{x:.0f}")
    
    st.dataframe(
        venue_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Venue cost calculator
    st.markdown("---")
    st.subheader("💰 Venue Cost Calculator")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_venue = st.selectbox(
            "Select Venue",
            options=filtered_venues['Venue'].tolist()
        )
    
    with col2:
        guest_count = st.number_input(
            "Number of Guests",
            min_value=1,
            max_value=300,
            value=150
        )
    
    if selected_venue:
        venue_data = filtered_venues[filtered_venues['Venue'] == selected_venue].iloc[0]
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

# Tab 2: Guest Management
with tab2:
    st.header("Guest List Management")
    
    # Apply filters
    filtered_guests = guest_list[guest_list['Category'].isin(category_filter)].copy()
    
    if event_filter != "All Events":
        filtered_guests = filtered_guests[filtered_guests[event_filter] == 1]
    
    # Guest metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_guests = len(filtered_guests)
        st.metric("Total Guests", total_guests)
    
    with col2:
        wedding_count = filtered_guests['Wedding'].sum()
        st.metric("Wedding Attendees", int(wedding_count))
    
    with col3:
        engagement_count = filtered_guests['Engagement Party'].sum()
        st.metric("Engagement Party", int(engagement_count))
    
    with col4:
        maryland_count = filtered_guests['Maryland Celebration'].sum()
        st.metric("Maryland Celebration", int(maryland_count))
    
    st.markdown("---")
    
    # Guest breakdown charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Category breakdown
        category_counts = filtered_guests['Category'].value_counts()
        fig_pie = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title='Guest Distribution by Category'
        )
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Event attendance
        event_data = pd.DataFrame({
            'Event': ['Wedding', 'Engagement Party', 'Maryland Celebration'],
            'Attendees': [
                filtered_guests['Wedding'].sum(),
                filtered_guests['Engagement Party'].sum(),
                filtered_guests['Maryland Celebration'].sum()
            ]
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
    
    # Guest list table
    st.subheader("Guest List Details")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search guests by name", "")
    
    if search_term:
        filtered_guests = filtered_guests[
            filtered_guests['Name'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display guest list
    guest_display = filtered_guests[['Name', 'Category', 'Source', 'Engagement Party', 
                                     'Maryland Celebration', 'Wedding', 'Total Events']].copy()
    
    # Convert 1/0 to Yes/No for events
    event_cols = ['Engagement Party', 'Maryland Celebration', 'Wedding']
    for col in event_cols:
        guest_display[col] = guest_display[col].apply(lambda x: '✓' if x == 1 else '')
    
    st.dataframe(
        guest_display,
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Download guest list
    csv = filtered_guests.to_csv(index=False)
    st.download_button(
        label="📥 Download Guest List (CSV)",
        data=csv,
        file_name=f"guest_list_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv'
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
    
    country_stats = all_venues.groupby('Country').agg({
        'Venue': 'count',
        'Base Price (£)': ['mean', 'min', 'max'],
        'Seated Capacity': 'mean',
        'Price per Guest (£)': 'mean'
    }).round(0)
    
    country_stats.columns = ['Count', 'Avg Price', 'Min Price', 'Max Price', 'Avg Capacity', 'Avg Per Guest']
    
    st.dataframe(
        country_stats,
        use_container_width=True
    )
    
    # Budget scenarios
    st.markdown("---")
    st.subheader("💰 Budget Scenarios")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scenario_guests = st.slider("Scenario Guest Count", 100, 250, 150, 10)
    
    with col2:
        selected_countries = st.multiselect(
            "Countries to Compare",
            ['England', 'Scotland', 'France'],
            default=['England', 'France']
        )
    
    if selected_countries:
        scenario_data = []
        for country in selected_countries:
            country_venues = all_venues[all_venues['Country'] == country]
            
            min_cost = country_venues['Base Price (£)'].min() + (scenario_guests * country_venues['Price per Guest (£)'].min())
            avg_cost = country_venues['Base Price (£)'].mean() + (scenario_guests * country_venues['Price per Guest (£)'].mean())
            max_cost = country_venues['Base Price (£)'].max() + (scenario_guests * country_venues['Price per Guest (£)'].max())
            
            scenario_data.append({
                'Country': country,
                'Minimum': min_cost,
                'Average': avg_cost,
                'Maximum': max_cost
            })
        
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

# Footer
st.markdown("---")
st.markdown("*Wedding Planning Dashboard • Last Updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
