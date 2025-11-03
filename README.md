# Wedding Planning Dashboard 💍

A comprehensive Streamlit dashboard for managing all aspects of wedding planning, including venue comparison, guest management, and seating arrangements.

## Features

### 1. 📊 Venue Comparison
- **Interactive venue analysis** across England, Scotland, and France
- **Price vs Capacity scatter plots** to find the best value venues
- **Cost calculator** for estimating total venue costs based on guest count
- **Filtering options** by country, capacity, and price range
- **Detailed venue information table** with all key attributes

### 2. 👥 Guest Management
- **Complete guest list tracking** for multiple events:
  - Wedding
  - Engagement Party
  - Maryland Celebration
- **Real-time headcount metrics** for each event
- **Guest category analysis** (Family, Friends, etc.)
- **Search functionality** to quickly find specific guests
- **Export capabilities** to download guest lists as CSV

### 3. 🪑 Table Seating Arrangement
- **Visual table layout** with drag-and-drop style interface
- **Configurable table settings** (number of tables, seats per table)
- **Auto-arrange options**:
  - Random shuffle for mixing guests
  - Group by category for keeping families/friends together
- **Capacity tracking** with visual indicators (🟢 full, 🟡 partial, 🔴 empty)
- **Export seating chart** as CSV for printing or sharing

### 4. 📈 Analytics & Insights
- **Event overlap analysis** showing which guests attend multiple events
- **Source analysis** tracking where guests come from (John B vs Darling)
- **Category deep dive** with attendance statistics
- **Budget scenario planning** for different guest counts
- **Country comparison** for venue pricing

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the dashboard:**
   ```bash
   streamlit run wedding_dashboard.py
   ```

3. **Access the dashboard:**
   - Open your browser and navigate to `http://localhost:8501`

## How to Use

### Getting Started
1. The dashboard automatically loads your wedding planning data from the Excel file
2. Use the sidebar filters to customize your view
3. Navigate between tabs to access different features

### Venue Comparison
1. **Filter venues** using the sidebar controls:
   - Select countries (England, Scotland, France)
   - Adjust capacity range slider
   - Set price range limits
2. **Analyze venues** using the interactive charts
3. **Calculate costs** by selecting a venue and entering guest count

### Guest Management
1. **Filter guests** by:
   - Event type (All, Wedding, Engagement, Maryland)
   - Guest category (Family, Friends, etc.)
2. **Search** for specific guests using the search box
3. **Export** the filtered list using the download button

### Table Seating
1. **Configure tables**:
   - Set number of tables
   - Set seats per table
   - Check capacity vs guest count
2. **Assign guests**:
   - Select a guest from dropdown
   - Assign to table number
   - Or use auto-arrange options
3. **Review layout** in the visual grid
4. **Export** seating chart as CSV

### Analytics
- Review comprehensive statistics and insights
- Adjust scenario parameters for budget planning
- Compare venue costs across countries

## Data Structure

The dashboard expects an Excel file with the following sheets:

1. **Master Invite List**: Guest information with event attendance
   - Columns: Name, Engagement Party, Maryland Celebration, Wedding, Category, Source

2. **England and Scotland**: Venue information for UK locations
   - Columns: Venue, Region/Country, Style, Capacity, etc.

3. **France**: Venue information for French locations
   - Similar structure to England/Scotland sheet

## Customization

### Modifying Price Estimates
The venue prices are currently estimated. To use real prices:
1. Add actual price columns to your Excel file
2. Modify the `load_wedding_data()` function to read these columns

### Adding New Events
To track additional events:
1. Add columns to the Master Invite List
2. Update the event filters in the Guest Management tab

### Changing Table Layout
Adjust the default table configuration in the session state initialization:
```python
'num_tables': 20,  # Change default number
'seats_per_table': 10  # Change default seats
```

## Tips

1. **Start with Venue Comparison** to narrow down your venue choices based on capacity and budget
2. **Use the Cost Calculator** to get accurate estimates for your shortlisted venues
3. **Review Analytics** regularly to understand guest patterns and optimize planning
4. **Export data frequently** to maintain backups and share with wedding planners
5. **Test different seating arrangements** using the auto-arrange features before finalizing

## Troubleshooting

### Dashboard won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.8+)

### Data not loading
- Verify the Excel file path is correct
- Ensure Excel file has the expected sheet names
- Check that data formats match expected structure

### Seating arrangement issues
- Clear browser cache if assignments aren't updating
- Reset assignments by using the Random Shuffle button

## Support

For questions or issues, please ensure your Excel file matches the expected format and all dependencies are properly installed.

---
*Built with Streamlit and ❤️ for your special day*
