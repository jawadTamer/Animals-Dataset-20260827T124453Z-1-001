# FarmGuard Field Mapping - Model Inputs vs Available Fields

## Model Required Inputs (15 fields)

| MODEL INPUT | AVAILABLE IN FARMGUARD | SOURCE | MISSING | DEMO DEFAULT ALLOWED? | NOTES |
|-------------|------------------------|--------|---------|------------------------|-------|
| species | YES (as animal_type) | livestock table | NO | N/A | Direct mapping: animal_type → species |
| breed | YES | livestock table | NO | N/A | Direct mapping |
| age_years | NO | livestock table has age_group | YES | YES | Derive from age_group or use default (e.g., 4.0) |
| weight_kg | NO | livestock table | YES | YES | Use species/breed average or default (e.g., cattle=600, sheep=70, goat=55) |
| sex | NO | livestock table | YES | YES | Use default (e.g., female) or add to schema |
| physiological_stage | NO | livestock table | YES | YES | Use default (e.g., lactating) or add to schema |
| health_status | NO | livestock table | YES | YES | Use default (healthy) or add to schema |
| latitude | NO | zone table (if exists) | YES | YES | Derive from zone_id or use farm location default |
| longitude | NO | zone table (if exists) | YES | YES | Derive from zone_id or use farm location default |
| elevation_m | NO | zone table (if exists) | YES | YES | Derive from zone_id or use default (e.g., 200) |
| climate_zone | NO | zone table (if exists) | YES | YES | Derive from zone_id or use default (e.g., Mediterranean) |
| temperature_c | YES | weather table | NO | N/A | Direct mapping: temperature → temperature_c |
| humidity_percent | YES | weather table | NO | N/A | Direct mapping: humidity → humidity_percent |
| wind_speed_m_s | NO | weather table | YES | YES | Use default (e.g., 3.0) or add to weather data |
| solar_radiation_w_m2 | NO | weather table | YES | YES | Use default (e.g., 300) or add to weather data |

## Summary

**Directly Available (4 fields):**
- species (as animal_type).
- breed
- temperature_c (as temperature)
- humidity_percent (as humidity)

**Missing - Require Defaults for Demo (11 fields):**
- age_years, weight_kg, sex, physiological_stage, health_status
- latitude, longitude, elevation_m, climate_zone
- wind_speed_m_s, solar_radiation_w_m2

## Recommended Demo Defaults

For hackathon demo, use these reasonable defaults:

| FIELD | DEMO DEFAULT | RATIONALE |
|-------|---------------|-----------|
| age_years | 4.0 | Typical adult animal age |
| weight_kg | species-specific (cattle=600, sheep=70, goat=55) | Species-average weight |
| sex | female | Common livestock sex |
| physiological_stage | lactating | Common production stage |
| health_status | healthy | Most common status |
| latitude | 40.0 | Representative Mediterranean latitude |
| longitude | 0.0 | Representative longitude |
| elevation_m | 200 | Typical farm elevation |
| climate_zone | Mediterranean | Common climate zone |
| wind_speed_m_s | 3.0 | Moderate wind speed |
| solar_radiation_w_m2 | 300 | Moderate solar radiation |

## Production Schema Extensions Required

For production deployment, FarmGuard database should be extended with:

**Livestock Table Additions:**
- age_years (float)
- weight_kg (float)
- sex (enum: male, female)
- physiological_stage (enum: lactating, dry, pregnant, growing)
- health_status (enum: healthy, minor_illness, recovering)

**Zone/Farm Table Additions:**
- latitude (float)
- longitude (float)
- elevation_m (float)
- climate_zone (enum: Mediterranean, Continental, Oceanic, Semi-arid)

**Weather Table Additions:**
- wind_speed_m_s (float)
- solar_radiation_w_m2 (float)
