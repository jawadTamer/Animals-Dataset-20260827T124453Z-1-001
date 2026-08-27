# FarmGuard Integration - Model Input Mapping

## Architecture Decision

**IMPORTANT:** The Python ML model (scikit-learn/joblib) cannot run directly in Angular or Supabase Edge Functions (which use JavaScript/TypeScript).

**Recommended Architecture for Hackathon:**
```
Angular Frontend
    ↓ HTTP API
Supabase Edge Function (TypeScript) OR Separate Python Backend
    ↓
Python Inference Service (FastAPI/Flask)
    ↓
Model Prediction (scikit-learn)
    ↓
JSON Response
    ↓
Angular UI
```

For the hackathon, the model should remain a separate Python inference service. The model artifacts and inference code are kept in this repository for integration.

## FarmGuard Database Schema (Current)

Based on the FarmGuard Supabase database, the livestock information contains:

**Livestock Table:**
- `animal_type` (e.g., cattle, sheep, goat)
- `breed` (e.g., Holstein, Merino)
- `quantity` (number of animals)
- `age_group` (e.g., calf, adult, senior)
- `zone_id` (farm/zone identifier)

**Weather/Context:**
- `temperature` (air temperature)
- `humidity` (relative humidity)
- `heat_index` (calculated heat index)
- `wet_bulb_temperature` (wet bulb temp)
- `precipitation` (rainfall)
- Other weather metrics

## Model Input Requirements

The current synthetic model requires:

**Required Fields:**
- `species` (cattle, sheep, goat)
- `breed` (specific breed name)
- `age_years` (numeric age in years)
- `weight_kg` (numeric weight in kg)
- `sex` (male/female)
- `physiological_stage` (lactating, dry, pregnant, growing)
- `health_status` (healthy, minor_illness, recovering)
- `latitude` (farm latitude)
- `longitude` (farm longitude)
- `elevation_m` (farm elevation in meters)
- `climate_zone` (Mediterranean, Continental, Oceanic, Semi-arid)
- `temperature_c` (air temperature in Celsius)
- `humidity_percent` (relative humidity percentage)
- `wind_speed_m_s` (wind speed in m/s)
- `solar_radiation_w_m2` (solar radiation in W/m²)

**Optional Fields:**
- `date` (measurement date, defaults to current date)

## Field Mapping

### Direct Mapping (FarmGuard → Model)

| FarmGuard Field | Model Field | Notes |
|----------------|-------------|-------|
| `animal_type` | `species` | Direct mapping |
| `breed` | `breed` | Direct mapping |
| `temperature` | `temperature_c` | Ensure Celsius |
| `humidity` | `humidity_percent` | Ensure percentage |

### Missing Fields (Not in FarmGuard Database)

| Model Field | Status | Recommended Action |
|-------------|--------|-------------------|
| `age_years` | **MISSING** | Derive from `age_group` or add to database |
| `weight_kg` | **MISSING** | Add to database or use species defaults |
| `sex` | **MISSING** | Add to database or make optional |
| `physiological_stage` | **MISSING** | Add to database or use defaults |
| `health_status` | **MISSING** | Add to database or default to 'healthy' |
| `latitude` | **MISSING** | Derive from `zone_id` or add to zone table |
| `longitude` | **MISSING** | Derive from `zone_id` or add to zone table |
| `elevation_m` | **MISSING** | Derive from `zone_id` or add to zone table |
| `climate_zone` | **MISSING** | Derive from lat/long or add to zone table |
| `wind_speed_m_s` | **MISSING** | Add to weather data |
| `solar_radiation_w_m2` | **MISSING** | Add to weather data |

### Field Transformations

**age_group → age_years:**
- calf → 0-2 years (use 1.0)
- adult → 2-8 years (use 4.0)
- senior → 8+ years (use 9.0)

**quantity:**
- Not used by model (model is per-animal)
- Use for batch predictions

**zone_id → location data:**
- Need zone table with: latitude, longitude, elevation, climate_zone
- If not available, use farm-level defaults

## Recommended Integration Strategy

### Option 1: Minimal Changes (Demo/Hackathon)

For the hackathon demo, use the following approach:

1. **Map available fields directly:**
   - `animal_type` → `species`
   - `breed` → `breed`
   - `temperature` → `temperature_c`
   - `humidity` → `humidity_percent`

2. **Use reasonable defaults for missing fields:**
   - `age_years`: 4.0 (adult)
   - `weight_kg`: Species defaults (cattle=500, sheep=70, goat=60)
   - `sex`: 'female' (common for dairy)
   - `physiological_stage`: 'lactating' (common for dairy)
   - `health_status`: 'healthy'
   - `latitude`, `longitude`: Use farm location (if available) or 35.0, 10.0
   - `elevation_m`: 200 (default)
   - `climate_zone`: 'Mediterranean' (default)
   - `wind_speed_m_s`: 3.0 (default)
   - `solar_radiation_w_m2`: 300 (default)

3. **Document clearly that these are defaults for demo purposes**

### Option 2: Database Schema Extension (Production)

For production deployment, extend the FarmGuard database:

**Add to livestock table:**
- `age_years` (numeric)
- `weight_kg` (numeric)
- `sex` (enum: male, female)
- `physiological_stage` (enum: lactating, dry, pregnant, growing)
- `health_status` (enum: healthy, minor_illness, recovering)

**Add to zone table:**
- `latitude` (numeric)
- `longitude` (numeric)
- `elevation_m` (numeric)
- `climate_zone` (enum: Mediterranean, Continental, Oceanic, Semi-arid)

**Add to weather data:**
- `wind_speed_m_s` (numeric)
- `solar_radiation_w_m2` (numeric)

## Weather Integration Architecture

```
┌─────────────────┐
│  Weather API    │
│  (External)     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ FarmGuard       │
│ Weather Store   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ AI Advisor      │
│ Context Layer   │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Animal Risk     │
│ Model           │
│ (ML)            │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Risk Prediction │
│ + Context       │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ Farmer          │
│ Recommendation  │
└─────────────────┘
```

**Model Inputs (ML Model):**
- temperature_c
- humidity_percent
- (wind_speed_m_s, solar_radiation_w_m2 if available)

**AI Advisor Context (Additional Weather):**
- heat_index (calculated from temp + humidity)
- wet_bulb_temperature
- precipitation
- wind_speed (if not used by model)
- forecast data

**Key Principle:**
The AI Advisor can use MORE weather context than the ML model. The model provides a risk prediction, and the AI Advisor combines this with additional weather context to generate farmer-friendly recommendations.

## Integration Code Example

```python
def farmguard_to_model_input(farmguard_data, weather_data, zone_data=None):
    """
    Convert FarmGuard database data to model input format.
    
    Args:
        farmguard_data: Dict with animal_type, breed, age_group, quantity
        weather_data: Dict with temperature, humidity
        zone_data: Optional dict with lat, lon, elevation, climate_zone
    
    Returns:
        Dict in model input format
    """
    # Direct mapping
    model_input = {
        'species': farmguard_data['animal_type'],
        'breed': farmguard_data['breed'],
        'temperature_c': weather_data['temperature'],
        'humidity_percent': weather_data['humidity'],
    }
    
    # Derive age from age_group
    age_map = {'calf': 1.0, 'adult': 4.0, 'senior': 9.0}
    model_input['age_years'] = age_map.get(farmguard_data.get('age_group', 'adult'), 4.0)
    
    # Use defaults for missing fields
    model_input['weight_kg'] = {
        'cattle': 500, 'sheep': 70, 'goat': 60
    }.get(model_input['species'], 500)
    
    model_input['sex'] = 'female'  # Default
    model_input['physiological_stage'] = 'lactating'  # Default
    model_input['health_status'] = 'healthy'  # Default
    
    # Use zone data if available, otherwise defaults
    if zone_data:
        model_input['latitude'] = zone_data.get('latitude', 35.0)
        model_input['longitude'] = zone_data.get('longitude', 10.0)
        model_input['elevation_m'] = zone_data.get('elevation_m', 200)
        model_input['climate_zone'] = zone_data.get('climate_zone', 'Mediterranean')
    else:
        model_input['latitude'] = 35.0
        model_input['longitude'] = 10.0
        model_input['elevation_m'] = 200
        model_input['climate_zone'] = 'Mediterranean'
    
    # Weather defaults
    model_input['wind_speed_m_s'] = weather_data.get('wind_speed', 3.0)
    model_input['solar_radiation_w_m2'] = weather_data.get('solar_radiation', 300)
    
    return model_input
```

## Limitations

1. **Missing animal metadata**: The current FarmGuard schema lacks detailed animal characteristics (age, weight, sex, physiological stage, health status). These are important for accurate heat-stress prediction.

2. **Missing location data**: Zone/farm location (latitude, longitude, elevation, climate zone) is needed for accurate predictions.

3. **Limited weather data**: Wind speed and solar radiation are not currently in the weather data but are used by the model.

4. **Default values**: Using defaults for missing fields reduces prediction accuracy. This is acceptable for demo/hackathon but not for production.

## Recommendation

**For Hackathon Demo:**
- Use Option 1 (minimal changes with defaults)
- Clearly document that defaults are used
- Acknowledge this as a limitation

**For Production:**
- Use Option 2 (database schema extension)
- Collect actual animal metadata
- Add location data to zones
- Add wind and solar radiation to weather data
