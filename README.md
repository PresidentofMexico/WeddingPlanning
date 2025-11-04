# Wedding Planning Dashboard 💍

A comprehensive Streamlit dashboard for managing all aspects of wedding planning, including venue comparison, guest management, and seating arrangements.

## ✨ What's New

### USD Currency Conversion & Clickable Venue Links (Latest)
🎉 **NEW**: All venue costs are now displayed in USD ($) for easy comparison!
- **Automatic currency conversion** from GBP (£) and EUR (€) to USD ($) using live exchange rates
- **Clickable venue names** that link directly to the venue's pricing source URL (opens in new tab)
- **Exchange rate script** (`convert_to_usd.py`) to refresh USD prices anytime with current rates
- **Seamless comparison** across England, Scotland, France, and United States venues

### Automatic Venue File Detection
The dashboard automatically detects and loads all venue CSV files in the repository! Simply add a new `{country}_csv.csv` file to the repository root, and it will be immediately available in the dashboard without any code changes. Currently supporting venues in **England, Scotland, United States, and France** with 62 total venues across all locations.

## Features

### 1. 📊 Venue Comparison
- **Interactive venue analysis** across multiple countries (auto-detected from CSV files)
- **USD pricing display** for all venues with automatic conversion from GBP/EUR
- **Clickable venue names** linking to official pricing sources (opens in new tab)
- **Automatic country detection** from filenames - supports unlimited countries/regions
- **Price vs Capacity scatter plots** to find the best value venues
- **Cost calculator** for estimating total venue costs based on guest count
- **Filtering options** by country, capacity, and price range (in USD)
- **Detailed venue information table** with all key attributes
- **Dynamic download options** for each country's venue data

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

## Currency Conversion & Exchange Rates

### Converting Venue Prices to USD

All venue prices are displayed in USD for easy comparison across different countries. The repository includes a currency conversion script that:

1. **Fetches live exchange rates** from free APIs (GBP→USD, EUR→USD)
2. **Converts pricing columns** in all venue CSV files
3. **Adds USD columns** to preserve original pricing
4. **Handles fallback rates** if APIs are unavailable

**To refresh exchange rates and update USD prices:**

```bash
python convert_to_usd.py
```

**What it does:**
- Processes `englandmore_csv.csv`, `englandscotland_csv.csv` (GBP → USD)
- Processes `france_csv.csv` (EUR → USD)
- Processes `unitedstates_csv.csv` (already in USD, standardizes column names)
- Creates or updates USD columns: `Published Venue Hire / Package (USD)`, `Per-Head / Menu From (USD)`, `Base Price (USD)`, `Price per Guest (USD)`
- Preserves original currency columns for reference

**Exchange Rate APIs Used:**
- Primary: `https://open.er-api.com/v6/latest/USD` (no authentication required)
- Fallback: `https://api.exchangerate-api.com/v4/latest/USD`
- If both fail: Uses conservative fallback rates (GBP: 1.27, EUR: 1.09)

**When to run the script:**
- After adding new venue data with GBP/EUR pricing
- Periodically to refresh with current exchange rates
- Before deploying updates to production

### Clickable Venue Links

Venue names in the dashboard are automatically rendered as clickable hyperlinks when a "Pricing Source URL(s)" column is present in the CSV. Clicking a venue name:
- Opens the venue's official pricing page in a new browser tab
- Allows quick access to detailed pricing information
- Helps verify and update pricing data

To add clickable links to new venues, include the `Pricing Source URL(s)` column in your CSV with the venue's website URL.

## Data Management

The dashboard supports both CSV and Excel file formats and provides flexible data management options.

### Automatic Venue File Detection

🎉 **New Feature**: The dashboard now automatically detects and loads all venue CSV files in the repository!

Simply add any venue CSV file with the naming pattern `*_csv.csv` to the repository root, and it will be automatically:
- **Detected** at dashboard startup
- **Loaded** and integrated into the venue dataset
- **Classified** by country/region based on the filename
- **Available** in all venue filters, charts, and analysis

**Currently detected files:**
- `wedding_roster_csv.csv` - Guest list with event attendance
- `englandscotland_csv.csv` - Venue information for England and Scotland
- `englandmore_csv.csv` - Additional England venues
- `france_csv.csv` - Venue information for France
- `unitedstates_csv.csv` - United States venues

**Filename to Country Mapping:**
- Files containing `unitedstates`, `usa`, or `us` → "United States"
- Files containing `englandscotland` → "England/Scotland"
- Files containing `england` or `englandmore` → "England"
- Files containing `scotland` → "Scotland"
- Files containing `france` → "France"
- Other files → Title case of filename (e.g., `italy_csv.csv` → "Italy")

### Uploading Custom CSV Files

You can upload your own CSV files through the dashboard:

1. **Click the "Upload CSV Files" section in the sidebar**
2. **Upload files for:**
   - Guest List CSV
   - Venue CSV Files (supports multiple files)
3. **Uploaded files are stored temporarily** during your session
4. **Click "Reset to Default Files"** to revert to the repository CSV files
5. **View detected files** in the sidebar showing filename and venue count per country

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
- **Pricing Source URL(s)**: URL to venue's pricing page (enables clickable venue names)

**Pricing columns** (original currency - GBP, EUR, or USD):
- **Published Venue Hire / Package (GBP)**: Published venue hire fee in British Pounds
- **Per-Head / Menu From (GBP)**: Per-guest pricing in British Pounds
- **Published Pricing**: General pricing information (EUR for France venues)
- Or equivalent columns in EUR (€) or USD ($)

**USD pricing columns** (auto-generated by `convert_to_usd.py`):
- **Published Venue Hire / Package (USD)**: Converted venue hire fee in US Dollars
- **Per-Head / Menu From (USD)**: Converted per-guest pricing in US Dollars
- **Base Price (USD)**: Base venue cost in USD
- **Price per Guest (USD)**: Per-guest pricing in USD

> **Note**: The dashboard prioritizes USD pricing for display. Original currency columns (GBP, EUR) are preserved for reference. Run `convert_to_usd.py` to generate or update USD columns from original pricing.

### Excel File Format (Legacy Support)

If using Excel files, the dashboard expects:
1. **Master Invite List** sheet: Guest information
2. **England and Scotland** sheet: UK venue information  
3. **France** sheet: French venue information

## Customization

### Adding New Venue Locations

**To add a new country/region:**

1. **Create a CSV file** following the venue format (see Data Structure below)
2. **Name it with pattern** `{country}_csv.csv` (e.g., `italy_csv.csv`, `spain_csv.csv`)
3. **Place it in the repository root** directory
4. **Restart the dashboard** - the file will be automatically detected and loaded!

No code changes required! The dashboard will:
- Auto-detect the new file
- Infer the country name from the filename
- Add it to the country filter dropdown
- Include it in all venue analysis and charts

### Using Your Own Data

1. **Prepare your CSV files** following the format described in Data Structure
2. **Option A - Upload via Dashboard:**
   - Use the "Upload CSV Files" section in the sidebar
   - Upload your guest list and venue CSVs (supports multiple venue files)
   - Changes are temporary (session only)
   - View detected files with venue counts in the sidebar

3. **Option B - Replace Repository Files:**
   - For guest list: Replace `wedding_roster_csv.csv`
   - For venues: Add or replace any `*_csv.csv` files in the repository root
   - If adding GBP or EUR pricing, run `python convert_to_usd.py` to generate USD columns
   - Changes are permanent for all users
   - All venue files are automatically detected and loaded

### Working with Venue Pricing

**To add or update venue prices:**

1. **Edit the CSV file** with pricing in the original currency (GBP, EUR, or USD)
2. **Add pricing columns** if not present:
   - For UK venues: `Published Venue Hire / Package (GBP)`, `Per-Head / Menu From (GBP)`
   - For France venues: `Published Pricing` (in EUR)
   - For US venues: Use USD columns directly
3. **Run the conversion script** to generate USD columns:
   ```bash
   python convert_to_usd.py
   ```
4. **Commit the updated CSV** files to the repository
5. **Restart the dashboard** to see the updated prices

The dashboard will display all prices in USD for consistent comparison across countries.

### Deployment Considerations

**Dependencies:**
- All required packages are listed in `requirements.txt`
- New dependency: `requests>=2.31.0` (for exchange rate API calls)
- The `convert_to_usd.py` script requires internet access to fetch live rates
- Fallback rates are used if APIs are unreachable

**For Streamlit Community Cloud or other deployment platforms:**
1. Ensure `requirements.txt` includes all dependencies
2. The dashboard will work with existing USD columns even without API access
3. To update exchange rates in deployment:
   - Run `convert_to_usd.py` locally with internet access
   - Commit the updated CSV files with new USD columns
   - Push to your repository to deploy

### Modifying Price Estimates
To use real venue prices instead of estimates:
1. Add pricing columns to your venue CSV files (in GBP, EUR, or USD)
2. Run `python convert_to_usd.py` to generate USD columns
3. The dashboard will automatically use these values instead of generating random estimates

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
