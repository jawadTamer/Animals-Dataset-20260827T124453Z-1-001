# Public Dataset Recommendations for FarmGuard Animal Heat-Risk Model

## Evaluation Results

I found several publicly available datasets. Here are the top candidates evaluated against FarmGuard requirements:

---

## RECOMMENDED DATASET #1: Environmental Data Initiative (EDI) - Dairy Cow Heat Stress

**Source:** https://portal.edirepository.org/nis/mapbrowse?packageid=edi.1406.1  
**DOI:** https://doi.org/10.6073/pasta/4a8cbfc4011ff759a0b5a3f08d7fc872  
**License:** Public Domain (CC0 1.0)  
**Species:** Dairy Cattle (Holstein)  
**Location:** Italian dairy farm  
**Time Period:** Summer 2021  
**Animals:** 102 cows

### Available Files
1. **health_events** (940.7 KB) - Health event records
2. **milk_yield** (2.7 MB) - Individual daily milk yield data
3. **sensor_data** (14.0 MB) - Ear-tag accelerometer sensor data (lying, chewing, activity)
4. **relative_humidity** (7.7 KB) - Humidity measurements
5. **temperature_degree** (7.8 KB) - Temperature measurements

### Features Available
✓ **Environmental:** Temperature, relative humidity  
✓ **Animal:** Individual cow IDs, behavioral data (lying, chewing, activity)  
✓ **Production:** Daily milk yield  
✓ **Health:** Health events (potential target variable)  
✓ **Temporal:** Daily measurements during heat waves  

### FarmGuard Requirements Match
- **Environmental features:** ✓ Temperature, humidity
- **Animal features:** ✓ Individual IDs, behavioral data
- **Farm/location:** ✗ No farm_id, zone_id, coordinates (single farm)
- **Target variable:** ✓ Health events (potential)
- **Data type:** ✓ Observational farm data (not experimental)

### Advantages
- Real farm data (not experimental)
- Has health events that could serve as target
- Includes behavioral sensor data
- Public domain license
- Adequate sample size (102 cows)

### Limitations
- Single farm only (no geographic diversity)
- Limited to dairy cattle (Holstein)
- No wind speed, solar radiation
- No animal metadata (age, weight, breed beyond Holstein)

---

## RECOMMENDED DATASET #2: Zenodo - Heart-Rate Monitoring of Dairy Cows at Pasture

**Source:** https://zenodo.org/records/15746212  
**Species:** Dairy Cattle  
**Location:** Malga Juribello, Trento province, Italy  
**File Size:** 28.4 MB  
**Format:** CSV

### Features Available
✓ **Environmental:** THI index, temperature, slope  
✓ **Animal:** Individual animal IDs  
✓ **Behavioral:** Heart-rate frequency, movement metrics  
✓ **Location:** Pasture environment with slope data  

### FarmGuard Requirements Match
- **Environmental features:** ✓ Temperature, THI
- **Animal features:** ✓ Individual IDs
- **Farm/location:** ✓ Slope/terrain data
- **Target variable:** ✗ Not explicitly stated
- **Data type:** ✓ Observational monitoring data

### Advantages
- Pasture environment (different from indoor)
- Includes terrain/slope data
- Heart-rate as physiological indicator
- Individual animal tracking

### Limitations
- No explicit heat-stress target variable
- No health events
- Limited environmental variables

---

## NOT RECOMMENDED

### Mendeley Data - HF Cross Cows
- **URL:** https://doi.org/10.17632/2d6r7j7rgf
- **Issue:** This appears to be the SAME dataset you already have (just published on Mendeley)
- **Same problems:** Experimental design, no legitimate target, data leakage

### HotPig - Pigs under Heat Stress
- **URL:** https://zenodo.org/records/15608130
- **Issue:** Wrong species (pigs, not cattle/livestock)
- **Issue:** Behavioral video analysis, not environmental prediction

### Global THI Projections
- **URL:** https://doi.org/10.26050/WDCC/THI
- **Issue:** Climate projection data, not animal-level observations
- **Issue:** No animal features or health outcomes

---

## FINAL RECOMMENDATION

**Download Dataset #1 (EDI Dairy Cow Heat Stress)**

This dataset best matches FarmGuard requirements:
- Real farm observational data
- Has potential target variable (health events)
- Includes environmental measurements
- Includes animal behavioral data
- Public domain license
- Adequate sample size

---

## Download Instructions

### Step 1: Access the Dataset
Visit: https://portal.edirepository.org/nis/mapbrowse?packageid=edi.1406.1

### Step 2: Download All Files
Download these 5 files:
1. health_events
2. milk_yield
3. sensor_data
4. relative_humidity
5. temperature_degree

### Step 3: Provide to Me
After downloading, place the files in your workspace and provide the file paths. I will then:
1. Audit the dataset
2. Clean and prepare it for modeling
3. Engineer features
4. Build the heat-risk prediction model
5. Evaluate and document

---

## Alternative: Create Synthetic Dataset

If you prefer not to download external data, I can create a realistic synthetic dataset that meets all FarmGuard requirements:
- Multiple farms with different locations
- Multiple animal species (cattle, sheep, goats)
- Complete environmental data (temperature, humidity, wind, solar radiation)
- Animal metadata (age, weight, breed, physiological stage)
- Synthetic heat-stress labels based on scientific THI thresholds
- Adequate sample size for modeling

**Note:** Synthetic data would be for demonstration/testing only, not suitable for production FarmGuard deployment.

---

## Your Decision

Please choose one option:
1. **Download EDI dataset** (recommended for real-world applicability)
2. **Download Zenodo dataset** (alternative with pasture data)
3. **Create synthetic dataset** (for demonstration only)
4. **Provide a different dataset** you have access to

Let me know your preference and I will proceed accordingly.
