# AI Insights Integration

## Overview
The Iowa Precision Agriculture system now includes **AI-powered insights** using Google Gemini AI to provide intelligent analysis based on your local datasets.

## Features

### 🤖 Location-Based AI Analysis
Click anywhere on the Iowa map to get comprehensive AI insights including:

1. **Current Situation Assessment**
   - Land use and crop analysis (from CDL 2023)
   - Vegetation health status (from NDVI)
   - Environmental conditions

2. **Crop Suitability & Recommendations**
   - Best crops for the location
   - Current crop performance analysis
   - Alternative crop suggestions

3. **Water Management**
   - Soil moisture analysis (SMAP data)
   - Rainfall adequacy assessment
   - Irrigation recommendations

4. **Vegetation Health Insights**
   - NDVI interpretation
   - Growth stage assessment
   - Stress indicators

5. **Environmental Factors**
   - Temperature impact (GridMET data)
   - Climate considerations
   - Seasonal patterns

6. **Actionable Recommendations**
   - Immediate actions needed
   - Management practices
   - Monitoring suggestions

7. **Future Outlook**
   - Expected trends
   - Risk factors
   - Optimization opportunities

## Datasets Analyzed

The AI uses all available Iowa local datasets:
- **Cropland Data Layer (CDL) 2023** - Current land use and crops
- **NDVI (Landsat)** - Vegetation health and biomass
- **GridMET Rainfall** - Precipitation data
- **GridMET Max Temperature** - Temperature patterns
- **SMAP Soil Moisture** - Volumetric water content
- **Landsat ET** - Evapotranspiration rates
- **NLCD 2021** - Land cover classification

## How to Use

### Step 1: Open AI Insights Panel
- Click the **🤖 robot icon** button in the top-right corner of the map
- The AI Insights panel will open on the right side

### Step 2: Select a Location
- Click anywhere within Iowa state boundaries on the map
- The system will gather all dataset information for that point

### Step 3: Review Analysis
- Current conditions are displayed first
- AI analysis provides comprehensive insights
- Recommendations are specific and actionable

### Step 4: Export or Refresh
- **📄 Export Report** - Save insights as a text file
- **🔄 Refresh** - Get updated analysis for the same location

## API Endpoint

### POST `/api/ai/location-insights`

Request body:
```json
{
  "latitude": 41.94,
  "longitude": -93.39,
  "data": {
    "datasets": {
      "Iowa CDL 2023": "Corn",
      "Iowa NDVI": "0.75",
      "Iowa GridMET Rainfall": "45.2",
      "Iowa GridMET Max Temp": "28.5",
      "Iowa SMAP Soil Moisture": "0.28",
      "Iowa Landsat ET": "5.3"
    }
  }
}
```

Response:
```json
{
  "location": {
    "latitude": 41.94,
    "longitude": -93.39
  },
  "recommendation": "Detailed AI analysis...",
  "source": "Google Gemini AI",
  "timestamp": "2024-01-15T10:30:00",
  "datasets_analyzed": ["Iowa CDL 2023", "Iowa NDVI", ...]
}
```

## Configuration

The Gemini API key is configured in `config.py`:

```python
gemini_api_key: str = ""  # Set in .env file: GEMINI_API_KEY=your_key_here
```

## UI Components

### AI Insights Button
- Location: Top-right corner of map
- Icon: 🤖 Robot emoji
- Function: Toggles AI insights panel

### AI Insights Panel
- Width: 450px
- Position: Fixed right side
- Features:
  - Gradient purple header
  - Scrollable content area
  - Current data display
  - AI analysis section
  - Action buttons

### Styling
- Primary color: Purple gradient (#667eea to #764ba2)
- Clean, modern design
- Responsive layout
- Smooth animations

## Technical Details

### Frontend (`ai-insights.js`)
- `initializeAIInsights()` - Initialize AI system
- `getAIInsights()` - Fetch AI analysis for location
- `gatherLocationData()` - Collect all dataset values
- `displayAIInsights()` - Render analysis results
- `exportInsights()` - Export as text file

### Backend (`main.py`)
- `/api/ai/location-insights` - Main AI endpoint
- `build_iowa_location_prompt()` - Build comprehensive prompt
- Uses Gemini 2.0 Flash model
- Temperature: 0.7 (balanced creativity/accuracy)

### AI Prompt Structure
The prompt includes:
1. Location coordinates
2. All available dataset values
3. Interpretation of NDVI ranges
4. Soil moisture status
5. Specific questions for analysis
6. Request for actionable recommendations

## Example Use Cases

### Scenario 1: Corn Field Analysis
- Click on corn field
- CDL shows "Corn"
- NDVI: 0.72 (healthy)
- Soil moisture: 0.26 (adequate)
- AI recommends: Continue current management, monitor for pests

### Scenario 2: Pasture Management
- Click on grassland
- NDVI: 0.45 (moderate)
- Low rainfall: 25mm
- Soil moisture: 0.18 (low)
- AI recommends: Irrigation needed, consider drought-resistant species

### Scenario 3: Crop Selection
- Click on bare field
- NDVI: 0.05 (no vegetation)
- High soil moisture: 0.32
- Recent rainfall: 60mm
- AI recommends: Suitable for rice or moisture-tolerant crops

## Performance

- **Response time**: 2-5 seconds (depends on Gemini API)
- **Data gathering**: < 500ms (local datasets)
- **UI rendering**: Instant
- **Export**: Instant

## Future Enhancements

Potential additions:
1. **Historical comparisons** - Compare current vs past conditions
2. **Multi-location analysis** - Compare several points at once
3. **Crop yield predictions** - AI-powered yield forecasting
4. **Pest & disease alerts** - Early warning system
5. **Fertilizer recommendations** - Precision nutrient management
6. **Seasonal planning** - Full-year crop rotation suggestions

## Troubleshooting

### AI Panel doesn't open
- Check browser console for errors
- Verify `ai-insights.js` is loaded
- Check that `initializeAIInsights()` was called

### No insights generated
- Ensure click is within Iowa boundaries
- Check Gemini API key is valid
- Verify `/api/ai/location-insights` endpoint is accessible
- Check browser network tab for errors

### Slow response
- Normal: Gemini AI can take 2-5 seconds
- Check internet connection
- Verify API quota not exceeded

### Empty dataset values
- Ensure datasets are loaded in layers panel
- Check that tiles are generating correctly
- Verify `/api/local-data/point` endpoint works

## Support

For issues or questions:
1. Check browser console logs
2. Verify server is running (`python main.py`)
3. Test `/api/ai/location-insights` endpoint directly
4. Check Gemini API status and quota

---

**Powered by Google Gemini AI 🤖**
