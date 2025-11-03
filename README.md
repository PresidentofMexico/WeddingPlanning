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
   streamlit run dashboard.py
   ```

3. **Access the dashboard:**
   - Open your browser and navigate to `http://localhost:8501`

## Data Management

The dashboard supports both CSV and Excel file formats and provides flexible data management options.

### Default Data Files

The dashboard automatically loads data from these CSV files in the repository:
- `wedding_roster_csv.csv` - Guest list with event attendance
- `englandscotland_csv.csv` - Venue information for England and Scotland
- `france_csv.csv` - Venue information for France

### Uploading Custom CSV Files

You can upload your own CSV files through the dashboard:

1. **Click the "Upload CSV Files" section in the sidebar**
2. **Upload files for:**
   - Guest List CSV
   - England/Scotland Venues CSV
   - France Venues CSV
3. **Uploaded files are stored temporarily** during your session
4. **Click "Reset to Default Files"** to revert to the repository CSV files

### Updating Repository Data

To permanently update the data in the repository:

1. **Make changes using the dashboard** or edit CSV files locally
2. **Download the updated CSV** using the download buttons in each tab
3. **Replace the corresponding file** in your local repository
4. **Commit and push** the changes to GitHub

**For Local Development:**
- Edit CSV files directly in your repository
- Changes take effect when you refresh the dashboard

**For Streamlit Community Cloud:**
- Streamlit Cloud cannot persist file changes to the repository
- Use download buttons to save updated CSVs
- Commit downloaded files to your repository manually

## How to Use

### Getting Started
1. The dashboard automatically loads wedding planning data from CSV files in the repository
2. Use the sidebar to upload custom CSV files or filter your data
3. Navigate between tabs to access different features
4. Download updated data to save changes permanently

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

The dashboard expects CSV or Excel files with the following structure:

### Guest List CSV Format

Required columns:
- **Name**: Guest name
- **Engagement Party**: 1 (attending) or 0 (not attending)
- **Maryland Celebration**: 1 (attending) or 0 (not attending)
- **Wedding**: 1 (attending) or 0 (not attending)
- **Category**: Guest category (e.g., Family, Friends, Fringe)
- **Source**: Source of invitation (e.g., John B, Darling)

Optional columns:
- **Total Events**: Automatically calculated if not provided
- **Guest ID**: Unique identifier for each guest

### Venue CSV Format

Required columns:
- **Venue**: Name of the venue
- **Region/Country**: Location information
- **Style**: Venue style/type
- **Seated Dinner Capacity**: Capacity for seated dinner (can include text)
- **Evening/Reception Capacity**: Capacity for reception (can include text)

Optional columns (recommended for full functionality):
- **Exclusive Use?**: Whether exclusive use is available
- **Bedrooms Onsite**: Number of bedrooms
- **Nearest Airports**: Nearby airports
- **Base Price (£)**: Base venue hire cost (auto-generated if not provided)
- **Price per Guest (£)**: Per-guest pricing (auto-generated if not provided)

### Excel File Format (Legacy Support)

If using Excel files, the dashboard expects:
1. **Master Invite List** sheet: Guest information
2. **England and Scotland** sheet: UK venue information  
3. **France** sheet: French venue information

## Customization

### Using Your Own Data

1. **Prepare your CSV files** following the format described in Data Structure
2. **Option A - Upload via Dashboard:**
   - Use the "Upload CSV Files" section in the sidebar
   - Upload your guest list and venue CSVs
   - Changes are temporary (session only)

3. **Option B - Replace Repository Files:**
   - Replace `wedding_roster_csv.csv` with your guest list
   - Replace `englandscotland_csv.csv` and/or `france_csv.csv` with your venues
   - Changes are permanent for all users

### Modifying Price Estimates
The venue prices are currently estimated. To use real prices:
1. Add `Base Price (£)` and `Price per Guest (£)` columns to your venue CSV files
2. The dashboard will automatically use these values instead of generating estimates

### Adding New Events
To track additional events:
1. Add new columns to your guest list CSV (e.g., "Rehearsal Dinner")
2. Use 1 for attending, 0 for not attending
3. The dashboard will automatically display the data
4. Update filters in the code if you want dedicated filter options

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
- Verify you're running: `streamlit run dashboard.py` (not wedding_dashboard.py)

### Data not loading
- Check that CSV files are in the repository root directory
- Verify CSV files have the correct column names (see Data Structure section)
- Check for encoding issues - the dashboard supports UTF-8, Latin-1, and CP1252
- Look for error messages at the top of the dashboard

### File upload not working
- Ensure file size is under 200MB
- Only CSV files are supported for upload
- Check that the CSV has the required columns
- Try refreshing the page and uploading again

### Charts not displaying
- Verify your CSV files have the necessary columns for the specific chart
- Check that numeric columns (like capacity, prices) contain valid numbers
- Some features require specific columns (e.g., pricing charts need Base Price and Price per Guest columns)

### Seating arrangement issues
- Clear browser cache if assignments aren't updating
- Reset assignments by using the Random Shuffle button

## Support

For questions or issues, please ensure your Excel file matches the expected format and all dependencies are properly installed.

---
*Built with Streamlit and ❤️ for your special day*
