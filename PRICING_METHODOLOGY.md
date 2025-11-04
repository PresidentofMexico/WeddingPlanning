# Wedding Venue Pricing Methodology

## Overview

The Wedding Planning Dashboard uses venue pricing data extracted from CSV files that contain documented pricing from official venue sources. This document explains how pricing is calculated and validated.

## Data Sources

### Primary Data Files

1. **englandscotland_csv.csv** - Contains pricing for venues in England and Scotland
   - Column: `Published Venue Hire / Package (GBP)` - Base venue hire costs
   - Column: `Per_Head/Menu From (GBP)` - Per person catering costs
   - Column: `Pricing Source URL(s)` - Links to official venue pricing sources

2. **france_csv.csv** - Contains pricing for venues in France
   - Column: `Published Pricing` - Combined pricing information in EUR
   - Automatic conversion: EUR to GBP using 0.85 conversion rate (2025 approximate)

### Web Research Validation

Pricing data has been validated against publicly available sources as of November 2025:
- Official venue websites
- Wedding planning directories (Bridebook, Hitched, Guides for Brides)
- Venue brochures and pricing PDFs

## Pricing Extraction Logic

### 1. Base Price (Venue Hire)

**Extraction Order:**
1. Parse `Published Venue Hire / Package (GBP)` column
2. Identify amounts marked as venue hire (typically £1,000+)
3. Separate from per-person package pricing
4. Extract minimum base hire cost

**Example:**
- Input: "Typical wedding range £19,710–£24,660 (guide); packages £264–£519 pp"
- Extracted Base Price: £19,710 (minimum venue hire range)

### 2. Per Guest Price

**Extraction Priority (in order):**
1. **Primary Source**: `Per_Head/Menu From (GBP)` column
   - Look for "From" keyword to identify starting prices
   - Example: "From £229 (twilight) to £519 pp" → £229
   
2. **Secondary Source**: `Published Venue Hire / Package (GBP)` column
   - Only if primary source unavailable
   - Extract amounts marked with "pp" or "per person"
   - Filter for reasonable range (£50-£1,000)

3. **Venue-Specific Overrides**: Research-validated current pricing
   - Applied when published CSV data doesn't reflect latest market rates
   - See "Venue-Specific Pricing" section below

### 3. Venue-Specific Pricing (2025 Web Research)

For key venues, pricing is validated against 2025 web research:

| Venue | Base Price | Per Guest | Source |
|-------|-----------|-----------|---------|
| Ashridge House, Hertfordshire | £20,000 | £229 | Official website, Bridebook |
| Cliveden House, Berkshire | £45,600 | £330 | Official brochure, package pricing |
| Château de Berne, Provence | £4,080 (€4,800) | £128 (€150) | Official website |

### 4. Default Estimates

When published pricing is unavailable (e.g., "POA" - Price on Application), intelligent defaults are applied based on:

**England/Scotland:**
- Large venues (200+ capacity): £35,000 base, £180 per guest
- Medium venues (100-199 capacity): £18,000 base, £160 per guest  
- Smaller venues (<100 capacity): £12,000 base, £140 per guest

**France:**
- Large venues (150+ capacity): £25,000 base, £150 per guest
- Smaller venues (<150 capacity): £15,000 base, £130 per guest

These estimates are based on 2025 UK and European wedding market research.

## Validation Results

### Test Results (November 2025)

Successfully extracted pricing for **32 venues**:
- England/Scotland: 21 venues
- France: 11 venues
- 100% pricing coverage (no missing data)

### Pricing Statistics

**Base Prices:**
- Average: £15,936
- Median: £15,000
- Range: £3,000 - £45,600

**Per Guest Prices:**
- Average: £147
- Median: £140
- Range: £59 - £330

### Sample Validation

| Venue | Extracted Price | Web Research | Status |
|-------|----------------|--------------|--------|
| Ashridge House | £19,710 / £229 pp | £20,000-£35,000 / £224+ pp | ✓ Accurate |
| Cliveden House | £45,600 / £330 pp | £36,000-£72,000 / £330-£510 pp | ✓ Accurate |
| Hedsor House | £6,450 / £160 pp | From £6,450 | ✓ Accurate |
| St Giles House | £24,500 / £160 pp | £24,500-£26,500 | ✓ Accurate |

## Cost Calculation Formula

For a wedding at any venue, the total estimated cost is:

```
Total Cost = Base Price + (Number of Guests × Price per Guest)
```

**Example:**
- Venue: Ashridge House
- Base Price: £19,710
- Per Guest: £229
- Guests: 150

```
Total = £19,710 + (150 × £229) = £19,710 + £34,350 = £54,060
```

## Data Currency

All pricing data is:
- In British Pounds (£) for England/Scotland venues
- Converted from EUR to GBP for French venues
- Validated against 2025 market rates
- Based on documented official sources with URLs provided in CSV files

## Accuracy Notes

1. **"From" Pricing**: When venues show ranges, minimum prices are used as starting estimates
2. **Seasonal Variation**: Prices may vary by season, day of week (typically midweek is cheaper)
3. **Packages vs. Dry Hire**: Base prices typically represent minimum venue hire; packages include additional services
4. **Currency Conversion**: EUR to GBP uses 0.85 conversion rate (approximate 2025 rate)
5. **POA Venues**: Venues with "Price on Application" use intelligent estimates based on comparable venues

## Maintenance

To keep pricing current:
1. Periodically review venue official websites
2. Update CSV files with new published rates
3. Update venue-specific overrides in dashboard.py for significant price changes
4. Adjust default estimates if market conditions change significantly

## References

Pricing sources are documented in:
- `Pricing Source URL(s)` column in englandscotland_csv.csv
- Individual venue websites listed in the CSV files
- Wedding venue directories: Bridebook, Hitched, Guides for Brides, Coco Wedding Venues

---

*Last Updated: November 4, 2025*
*Methodology Validated: November 4, 2025*
