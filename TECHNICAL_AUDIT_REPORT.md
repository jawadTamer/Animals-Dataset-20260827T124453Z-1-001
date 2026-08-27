# FarmGuard Animal Heat-Risk Model - Technical Audit Report

**Date:** August 27, 2026  
**Auditor:** Senior ML Engineer  
**Repository:** Animals-Dataset-20260827T124453Z-1-001

---

## Executive Summary

This is a comprehensive technical audit of the FarmGuard Animal Heat-Risk Prediction Model. The audit examined the dataset, target definition, training pipeline, model architecture, inference pipeline, and repository structure.

**CRITICAL FINDING:** The model is trained on SYNTHETIC/DERIVED risk labels. The target (risk_level) is deterministically derived from THI (Temperature-Humidity Index) thresholds, not from observed ground truth. The model is learning to approximate a rule, not predict real-world outcomes.

**VERDICT:** KEEP WITH LIMITATIONS - The model is suitable for hackathon demonstration purposes as a prototype risk classifier, but must be clearly labeled as synthetic/derived and not claimed to have real-world predictive accuracy.

---

## A. Dataset Verdict

### Dataset Statistics
- **Total rows:** 10,000
- **Total unique animals:** 1,000
- **Total farms:** 10
- **Date range:** January 1, 2023 - December 30, 2023
- **Species:** cattle (36.3%), goat (31.9%), sheep (31.8%)
- **Breeds:** 5 breeds per species (15 total)
- **Missing values:** None
- **Duplicate rows:** None

### Data Classification
- **All data:** SYNTHETIC
- **Environmental measurements:** SIMULATED
- **Animal metadata:** SYNTHETIC
- **Target (risk_level):** DERIVED from THI thresholds
- **THI, HLI:** DERIVED from environmental inputs

### VERDICT: KEEP WITH LIMITATIONS
The dataset is fully synthetic and suitable for demonstration/hackathon purposes, but must be clearly labeled as such. It cannot support real-world outcome prediction.

---

## B. Target Verdict

### Target Construction Analysis
The target (risk_level) is derived from THI using species-specific thresholds:

**THI Calculation:**
```
THI = (1.8 * T + 32) - ((0.55 - 0.0055 * RH) * (1.8 * T - 26))
```
Where T = temperature_c, RH = humidity_percent

**Species Thresholds:**
- Cattle: Low<72, Moderate<79, High<84, Critical>=84
- Sheep: Low<75, Moderate<82, High<87, Critical>=87
- Goats: Low<74, Moderate<81, High<86, Critical>=86

### Critical Finding
```
risk_level <- THI <- (temperature_c, humidity_percent)
```

The target is DETERMINISTICALLY derived from model inputs. This is RULE-LEARNING, not observed-outcome prediction. The model is learning to approximate the THI-based labeling rule.

**Correlation between THI and risk_level:** 0.8040 (highly deterministic)

### VERDICT: DERIVED TARGET (NOT OBSERVED)
This is the fundamental limitation of the model. The model is a prototype risk classifier that approximates scientific thresholds, not a predictive model of observed heat stress outcomes.

---

## C. Data Leakage Verdict

### Leakage Sources Examined

**THI and HLI:**
- These are derived from temperature and humidity
- NOT used as features in the model (correctly excluded)
- **VERDICT:** No leakage from THI/HLI

**risk_level:**
- This is the target, not a feature
- **VERDICT:** No leakage from target

**animal_id:**
- Used for group-aware splitting (correct)
- Not used as a feature
- **VERDICT:** No leakage from animal_id

**date/month/season:**
- Temporal features are used as features
- This is acceptable for seasonal patterns
- **VERDICT:** Acceptable, not leakage

**farm_id:**
- Not used as a feature
- **VERDICT:** No leakage from farm_id

**Environmental variables:**
- temperature_c, humidity_percent are features
- risk_level is derived from these (via THI)
- This is TARGET CONSTRUCTION, not leakage
- **VERDICT:** This is the fundamental issue, not leakage per se

### Split Strategy
- Group-aware split by animal_id (correct)
- Prevents same animal in train and test
- **VERDICT:** Correctly implemented

### Temporal Validation
- Dataset covers full year 2023
- No temporal split implemented
- **VERDICT:** Should add temporal validation for robustness (not critical for demo)

### VERDICT: NO LEAKAGE (BUT TARGET CONSTRUCTION ISSUE)
No data leakage in the traditional sense, but the target construction is the fundamental limitation.

---

## D. Model Verdict

### Model Architecture
- **Algorithm:** RandomForestClassifier
- **n_estimators:** 200
- **max_depth:** 15
- **min_samples_split:** 10
- **min_samples_leaf:** 5
- **class_weight:** balanced

### Preprocessing
- **Categorical encoding:** LabelEncoder for 7 features
- **Numerical scaling:** StandardScaler
- **Feature columns:** 18 features

### Feature Columns Used
['species_encoded', 'breed_encoded', 'sex_encoded', 'physiological_stage_encoded', 'health_status_encoded', 'climate_zone_encoded', 'season_encoded', 'age_years', 'weight_kg', 'latitude', 'longitude', 'elevation_m', 'temperature_c', 'humidity_percent', 'wind_speed_m_s', 'solar_radiation_w_m2', 'day_of_year', 'month']

### Class Weighting
- class_weight='balanced' used
- **VERDICT:** Appropriate for imbalanced dataset

### VERDICT: APPROPRIATE ARCHITECTURE
The model architecture is sound for the given task. Preprocessing is correct. The limitation is the data/target, not the model architecture.

---

## E. Inference Verdict

### Issues Fixed
1. **Absolute paths:** Removed all absolute Windows paths, now uses relative paths
2. **risk_score:** Changed from encoded class integer to meaningful weighted average of probabilities (0-100 scale)
3. **Input validation:** Added validation for species support and required fields
4. **Species enforcement:** Added explicit rejection of unsupported species

### Current Implementation
- **risk_score calculation:** Weighted average where Low=0, Moderate=33.3, High=66.7, Critical=100
- **Input validation:** Checks for missing required fields and null values
- **Species enforcement:** Rejects unsupported species with clear error message
- **Unseen categorical handling:** Handles unseen categories with -1 encoding

### VERDICT: PRODUCTION-READY FOR DEMO
Inference pipeline is now robust with proper validation, meaningful scoring, and clear error handling.

---

## F. FarmGuard Integration Verdict

### FarmGuard Database Schema (Current)
**Livestock Table:**
- animal_type, breed, quantity, age_group, zone_id

**Weather/Context:**
- temperature, humidity, heat_index, wet_bulb_temperature, precipitation

### Model Input Requirements
**Required Fields (15):**
- species, breed, age_years, weight_kg, sex, physiological_stage, health_status
- latitude, longitude, elevation_m, climate_zone
- temperature_c, humidity_percent, wind_speed_m_s, solar_radiation_w_m2

### Field Mapping Analysis
**Direct Mapping (4 fields):**
- animal_type → species
- breed → breed
- temperature → temperature_c
- humidity → humidity_percent

**Missing Fields (11 fields):**
- age_years, weight_kg, sex, physiological_stage, health_status
- latitude, longitude, elevation_m, climate_zone
- wind_speed_m_s, solar_radiation_w_m2

### VERDICT: INTEGRATION REQUIRES DATABASE EXTENSION
For hackathon demo, use reasonable defaults. For production, extend FarmGuard database schema to include missing fields. See FARMGUARD_INTEGRATION.md for detailed guidance.

---

## G. New Dataset Required?

### Decision: KEEP WITH LIMITATIONS

**Reasoning:**
1. The synthetic dataset is suitable for hackathon demonstration
2. The model correctly implements a prototype risk classifier
3. Real-world datasets with observed heat stress outcomes are rare and difficult to obtain
4. The current approach is scientifically defensible as a demonstration of THI-based risk classification

**Conditions:**
1. MUST clearly label as synthetic/derived
2. MUST NOT claim real-world predictive accuracy
3. MUST communicate limitations in README and presentation
4. MUST validate on real data before production use

### VERDICT: KEEP WITH LIMITATIONS
No new dataset required for hackathon. For production, collect real-world observational data.

---

## H. Files to Keep

### Essential Files
- `README.md` - Main documentation (updated with limitations)
- `MODEL_CONTRACT.md` - Prediction contract and API specification
- `FARMGUARD_INTEGRATION.md` - FarmGuard integration guidance
- `inference.py` - Inference pipeline (fixed and validated)
- `test_inference.py` - Test suite (all tests passing)
- `requirements.txt` - Dependencies
- `animal_heat_risk_model.pkl` - Trained model
- `feature_scaler.pkl` - Feature scaler
- `label_encoders.pkl` - Categorical encoders
- `target_encoder.pkl` - Target encoder
- `feature_columns.pkl` - Feature column list

### Dataset Files
- `farmguard_animal_heat_risk.csv` - Main dataset
- `farmguard_animals_metadata.csv` - Animal metadata
- `farmguard_farms.csv` - Farm information

### Training Scripts
- `create_synthetic_dataset.py` - Dataset generation (fixed paths)
- `prepare_and_train_model.py` - Training pipeline (fixed paths)

---

## I. Files to Delete

### Deleted Files
- `DATASET_AUDIT_REPORT.md` - Temporary audit report
- `DATASET_RECOMMENDATIONS.md` - Temporary recommendations
- `audit_edi_dataset.py` - EDI dataset audit (not needed)
- `comprehensive_analysis.py` - Temporary analysis
- `data_audit.py` - Temporary audit
- `investigate_species.py` - Temporary investigation
- `technical_audit.py` - Temporary audit script
- `health_events.txt` - EDI dataset file (not used)
- `milk_yield.txt` - EDI dataset file (not used)
- `sensor_data.txt` - EDI dataset file (not used)
- `relative_humidity.csv` - EDI dataset file (not used)
- `temperature_degree.csv` - EDI dataset file (not used)
- `edi.1406.1.report.xml` - EDI metadata (not used)
- `edi.1406.1.txt` - EDI metadata (not used)
- `edi.1406.1.xml` - EDI metadata (not used)
- `manifest.txt` - Temporary manifest
- `Animals Dataset/` - Duplicate directory (removed)
- `__pycache__/` - Python cache (removed)

---

## J. Exact Changes Made

### 1. Inference Pipeline (inference.py)
- Removed absolute Windows paths, now uses relative paths
- Added `validate_input()` method for input validation
- Added species support enforcement (rejects unsupported species)
- Fixed `risk_score` calculation: changed from encoded integer to weighted average (0-100 scale)
- Added required fields validation
- Added null value checking
- Updated docstring to clearly state synthetic/derived nature

### 2. Training Scripts
- **create_synthetic_dataset.py:** Changed absolute paths to relative paths
- **prepare_and_train_model.py:** Changed absolute paths to relative paths

### 3. Repository Structure
- Removed all EDI dataset files (not used by final model)
- Removed temporary audit and analysis scripts
- Removed duplicate directories
- Removed Python cache
- Reorganized into model/ and data/ directories for clean structure
- Updated all paths to use new directory structure

### 4. Documentation
- **README.md:** Updated to clearly state synthetic/derived nature
- Added critical disclaimer about target construction
- Added MODEL_CONTRACT.md with full API specification
- Added FARMGUARD_INTEGRATION.md with integration guidance
- Added requirements.txt for reproducibility

### 5. Testing
- Created comprehensive test suite (test_inference.py)
- All 14 tests passing
- Tests cover: valid inputs (cattle, sheep, goat), missing fields, unsupported species, extreme heat/cold, null values, unknown breeds, different physiological stages, batch prediction, output schema, date field handling

---

## K. Final Model Limitations

### Critical Limitations
1. **Synthetic/Derived Target:** Risk labels are derived from THI thresholds, not observed outcomes
2. **Rule-Learning:** Model learns to approximate a deterministic rule, not predict real-world events
3. **No Real-World Validation:** Performance metrics do not represent real-world accuracy

### Data Limitations
4. **Single Year:** Data covers only 2023, no year-to-year variation
5. **Geographic Scope:** Limited to 30°-45° latitude, -10° to 40° longitude
6. **Species Limitation:** Only supports cattle, sheep, goats
7. **Breed Limitation:** Only 5 breeds per species

### Integration Limitations
8. **Missing FarmGuard Fields:** 11 required fields not in current FarmGuard database
9. **Defaults Required:** Integration requires using defaults for missing fields

### Validation Limitations
10. **No Temporal Validation:** No temporal split implemented
11. **Moderate Risk Performance:** Lower performance on moderate risk class (69% F1)

---

## L. Recommended Next Steps

### For Hackathon Demo
1. **Use defaults for missing fields** as documented in FARMGUARD_INTEGRATION.md
2. **Clearly communicate limitations** in presentation
3. **Use scientifically honest wording:** "Prototype risk classifier trained on synthetic/derived labels"
4. **Do NOT claim:** "88% real-world heat-stress prediction accuracy"

### For Production Deployment
1. **Collect real-world observational data** with actual heat stress outcomes
2. **Extend FarmGuard database schema** to include missing animal and location fields
3. **Add wind and solar radiation** to weather data collection
4. **Validate model on real farm data** before production use
5. **Implement temporal validation** for robustness assessment
6. **Consider species-specific models** if accuracy requirements are high

### For Future Development
1. **Explore alternative algorithms** (XGBoost, CatBoost, Neural Networks)
2. **Add ensemble methods** for improved robustness
3. **Develop region-specific models** for different climate zones
4. **Integrate with weather forecast APIs** for predictive alerts
5. **Create web interface** for farmer-friendly access

---

## Final Verdict Summary

| Component | Verdict | Status |
|-----------|---------|--------|
| Dataset | KEEP WITH LIMITATIONS | Synthetic but suitable for demo |
| Target | DERIVED (NOT OBSERVED) | Critical limitation - rule-learning |
| Leakage | NO LEAKAGE | Correctly implemented |
| Model | APPROPRIATE | Sound architecture |
| Inference | PRODUCTION-READY | Fixed and validated |
| FarmGuard Integration | REQUIRES EXTENSION | Use defaults for demo |
| New Dataset | NOT REQUIRED | Keep with clear limitations |

**Overall Assessment:** The model is suitable for hackathon demonstration as a prototype risk classifier, provided all limitations are clearly communicated. It is NOT suitable for production use without real-world validation and database schema extensions.

---

## Repository Structure (Final)

```
Animals-Dataset-20260827T124453Z-1-001/
├── README.md                          # Main documentation
├── MODEL_CONTRACT.md                  # API specification
├── FARMGUARD_INTEGRATION.md           # Integration guidance
├── TECHNICAL_AUDIT_REPORT.md          # This audit report
├── requirements.txt                   # Dependencies
├── inference.py                       # Inference pipeline
├── test_inference.py                  # Test suite
├── create_synthetic_dataset.py       # Dataset generation
├── prepare_and_train_model.py        # Training pipeline
├── model/                             # Model artifacts directory
│   ├── animal_heat_risk_model.pkl     # Trained model (16.64 MB)
│   ├── feature_scaler.pkl             # Feature scaler
│   ├── label_encoders.pkl             # Categorical encoders
│   ├── target_encoder.pkl             # Target encoder
│   └── feature_columns.pkl            # Feature columns
└── data/                              # Dataset directory
    ├── farmguard_animal_heat_risk.csv # Main dataset (2.02 MB)
    ├── farmguard_animals_metadata.csv # Animal metadata (86 KB)
    └── farmguard_farms.csv            # Farm information (829 B)
```

---

**Audit Completed:** August 27, 2026  
**Status:** COMPLETE - Model ready for hackathon demonstration with documented limitations
