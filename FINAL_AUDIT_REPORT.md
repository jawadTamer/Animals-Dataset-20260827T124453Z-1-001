# FarmGuard Animal Heat-Risk Model - Final Technical Audit Report

**Date:** August 27, 2026  
**Auditor:** Senior ML Engineer  
**Repository:** Animals-Dataset-20260827T124453Z-1-001  
**Purpose:** Final technical audit and cleanup for FortyGuard Hackathon'26 integration

---

## Executive Summary

This is a comprehensive final technical audit of the FarmGuard Animal Heat-Risk Prediction Model. The audit examined the dataset generation, training pipeline, model architecture, inference safety, FarmGuard compatibility, and repository structure.

**CRITICAL FINDING:** The model is trained on SYNTHETIC/DERIVED risk labels. The target (risk_level) is deterministically derived from THI (Temperature-Humidity Index) thresholds, not from observed ground truth. The model learns to approximate a rule, not predict real-world outcomes.

**FINAL VERDICT:** READY FOR HACKATHON DEMO WITH CLEAR LIMITATIONS - The model is suitable for hackathon demonstration as a prototype risk classifier, provided all limitations are clearly communicated. It is NOT suitable for production use without real-world validation and database schema extensions.

---

## A. Dataset Verdict

### Dataset Statistics (Verified)
- **Total rows:** 10,000
- **Total unique animals:** 1,000
- **Total farms:** 10
- **Date range:** January 1, 2023 - December 30, 2023
- **Species distribution:** cattle (36.31%), goat (31.89%), sheep (31.80%)
- **Risk level distribution:** Low (61.50%), Moderate (15.75%), Critical (12.61%), High (10.14%)
- **Missing values:** None
- **Duplicate rows:** None

### Data Classification
- **All data:** SYNTHETIC
- **Environmental measurements:** SIMULATED with seasonal variation
- **Animal metadata:** SYNTHETIC
- **Target (risk_level):** DERIVED from THI thresholds with 10% noise
- **THI, HLI:** DERIVED from environmental inputs

### Target Derivation Verification
**From create_synthetic_dataset.py lines 99-147:**
- THI calculated from temperature_c and humidity_percent
- risk_level derived from THI thresholds (species-specific)
- 10% noise added for realism
- THI-risk_level correlation: 0.8040 (highly deterministic)

**VERDICT: SYNTHETIC/DERIVED LABELS - NOT OBSERVED OUTCOMES**

---

## B. Model Verdict

### Model Configuration (Verified)
- **Algorithm:** RandomForestClassifier
- **n_estimators:** 200
- **max_depth:** 15
- **min_samples_split:** 10
- **min_samples_leaf:** 5
- **class_weight:** balanced
- **random_state:** 42

### Preprocessing (Verified)
- **Categorical encoding:** LabelEncoder for 7 features
- **Numerical scaling:** StandardScaler
- **Feature columns:** 18 features
- **Temporal features:** day_of_year, month, season derived from date

### Feature Columns Used (Verified)
['species_encoded', 'breed_encoded', 'sex_encoded', 'physiological_stage_encoded', 'health_status_encoded', 'climate_zone_encoded', 'season_encoded', 'age_years', 'weight_kg', 'latitude', 'longitude', 'elevation_m', 'temperature_c', 'humidity_percent', 'wind_speed_m_s', 'solar_radiation_w_m2', 'day_of_year', 'month']

### Performance Metrics (Verified)
- **Accuracy:** 88.05%
- **Macro F1:** 82.78%
- **Weighted F1:** 88.15%

**Per-Class Performance:**
- Critical: Precision=0.94, Recall=0.90, F1=0.92
- High: Precision=0.70, Recall=0.82, F1=0.76
- Low: Precision=0.95, Recall=0.94, F1=0.95
- Moderate: Precision=0.70, Recall=0.68, F1=0.69

**Confusion Matrix:**
```
[[ 236   26    0    1]
 [  15  174    1   23]
 [   0    1 1207   76]
 [   0   46   62  233]]
```

**VERDICT: APPROPRIATE ARCHITECTURE**
The model architecture is sound for the given task. Preprocessing is correct. The limitation is the data/target, not the model architecture.

---

## C. Data Leakage Verdict

### Leakage Sources Examined (Verified)

**THI and HLI:**
- These are derived from temperature and humidity
- NOT used as features in the model (correctly excluded at line 49-50)
- **VERDICT:** No leakage from THI/HLI

**risk_level:**
- This is the target, not a feature
- **VERDICT:** No leakage from target

**animal_id:**
- Used for group-aware splitting (correct)
- Not used as a feature
- **VERDICT:** No leakage from animal_id

**farm_id:**
- Not used as a feature
- **VERDICT:** No leakage from farm_id

**date/month/season:**
- Temporal features are used as features
- This is acceptable for seasonal patterns
- **VERDICT:** Acceptable, not leakage

**Environmental variables:**
- temperature_c, humidity_percent are features
- risk_level is derived from these (via THI)
- This is TARGET CONSTRUCTION, not leakage
- **VERDICT:** This is the fundamental issue, not leakage per se

### Split Strategy (Verified)
- Group-aware split by animal_id (correct)
- 800 training animals, 200 test animals
- No animal exists in both train and test
- **VERDICT:** Correctly implemented

### Preprocessing Leakage (Verified)
- Scaler fitted ONLY on training data (line 109)
- Test data transformed using training scaler (line 110)
- **VERDICT:** Correctly implemented

**VERDICT: NO DATA LEAKAGE (BUT TARGET CONSTRUCTION ISSUE)**
No data leakage in the traditional sense, but the target construction is the fundamental limitation.

---

## D. Validation Verdict

### Train/Test Split (Verified)
- **Training samples:** 7,899
- **Test samples:** 2,101
- **Training animals:** 800
- **Test animals:** 200
- **Group-aware:** Yes, by animal_id
- **No overlap:** Verified

### Metrics Calculated (Verified)
- Accuracy: 88.05%
- Macro F1: 82.78%
- Weighted F1: 88.15%
- Per-class precision/recall/F1: Calculated
- Confusion matrix: Generated
- Critical-class recall: 90%

**VERDICT: VALIDATION CORRECTLY IMPLEMENTED**
All metrics calculated correctly on held-out test animals. No inflation detected.

---

## E. Inference Safety Verdict

### Safety Features Implemented (Verified)
- **Species enforcement:** Rejects unsupported species (line 76-82)
- **Required fields validation:** Checks for missing fields (line 85-87)
- **Null value checking:** Rejects null values (line 90-92)
- **Unseen categorical handling:** Encodes as -1 (line 134-136)
- **Input validation:** validate_input() method (line 66-92)
- **Error messages:** Clear ValueError messages

### Output Schema (Verified)
- risk_level: String (Low/Moderate/High/Critical)
- risk_score: Number (0-100, weighted average of probabilities)
- confidence: Number (0-1, max probability)
- probabilities: Dictionary with all 4 risk levels

### Preprocessing Consistency (Verified)
- Feature columns match training exactly
- Categorical encoding matches training
- Numerical scaling uses training scaler
- Temporal feature derivation matches training

**VERDICT: PRODUCTION-READY FOR DEMO**
Inference pipeline is robust with proper validation, meaningful scoring, and clear error handling.

---

## F. FarmGuard Integration Verdict

### FarmGuard Database Schema (Current)
**Livestock Table:**
- animal_type, breed, quantity, age_group, zone_id

**Weather/Context:**
- temperature, humidity, heat_index, wet_bulb_temperature, precipitation

### Model Input Requirements (15 fields)
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

### Architecture Decision
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

**VERDICT: INTEGRATION REQUIRES DATABASE EXTENSION**
For hackathon demo, use reasonable defaults. For production, extend FarmGuard database schema to include missing fields. See FARMGUARD_INTEGRATION.md for detailed guidance.

---

## G. Files Deleted

### Deleted During Audit
- `final_comprehensive_audit.py` - Temporary audit script
- `__pycache__/` - Python cache directory

### Previously Deleted (from earlier cleanup)
- EDI dataset files (health_events.txt, milk_yield.txt, sensor_data.txt, etc.)
- Temporary audit scripts (audit_edi_dataset.py, technical_audit.py, etc.)
- Duplicate directories and caches

---

## H. Files Modified

### Modified During Final Audit
1. **prepare_and_train_model.py**
   - Changed dataset path: `'farmguard_animal_heat_risk.csv'` → `'data/farmguard_animal_heat_risk.csv'`
   - Changed artifact paths: `'animal_heat_risk_model.pkl'` → `'model/animal_heat_risk_model.pkl'` (and all other artifacts)

2. **create_synthetic_dataset.py**
   - Changed save paths: `'farmguard_animals_metadata.csv'` → `'data/farmguard_animals_metadata.csv'` (and all other data files)

3. **FARMGUARD_INTEGRATION.md**
   - Added architecture decision section documenting Angular → Supabase → Python service architecture

4. **TECHNICAL_AUDIT_REPORT.md**
   - Updated test count: 9 tests → 14 tests
   - Updated repository structure with model/ and data/ directories
   - Updated file paths to reflect new directory structure

---

## I. Files Added

### Added During Final Audit
None (all files were modified, not added)

### Previously Added (from earlier work)
- `MODEL_CONTRACT.md` - API specification
- `FARMGUARD_INTEGRATION.md` - Integration guidance
- `TECHNICAL_AUDIT_REPORT.md` - Initial audit report
- `requirements.txt` - Dependencies
- `test_inference.py` - Test suite

---

## J. Final Model Limitations

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
10. **No Temporal Validation:** No temporal split implemented (not critical for demo)
11. **Moderate Risk Performance:** Lower performance on moderate risk class (69% F1)

### Architecture Limitations
12. **Python Dependency:** Model requires Python/scikit-learn/joblib, cannot run directly in Angular or Supabase Edge Functions
13. **Separate Service Required:** Must deploy as separate Python inference service

---

## K. Hackathon Integration Readiness

### Status: READY WITH CLEAR LIMITATIONS

**Conditions for Hackathon Use:**
1. ✅ Model artifacts properly organized in `model/` directory
2. ✅ Dataset files properly organized in `data/` directory
3. ✅ Inference pipeline with proper validation and error handling
4. ✅ Comprehensive test suite (14 tests, all passing)
5. ✅ Clear documentation of synthetic/derived nature
6. ✅ Architecture decision documented (Python service required)
7. ✅ FarmGuard integration guidance provided
8. ✅ All limitations clearly communicated

**Required Communication:**
- Must clearly state: "Prototype risk classifier trained on synthetic/derived labels"
- Must NOT claim: "88% real-world heat-stress prediction accuracy"
- Must document: 11 missing FarmGuard fields require defaults or schema extension
- Must document: Python inference service required (cannot run in Angular/Supabase directly)

**Recommended Hackathon Architecture:**
- Angular frontend calls Python inference service via HTTP API
- Python service loads model artifacts and returns predictions
- For demo, use documented defaults for missing FarmGuard fields

---

## Final Repository Structure

```
Animals-Dataset-20260827T124453Z-1-001/
├── README.md                          # Main documentation
├── MODEL_CONTRACT.md                  # API specification
├── FARMGUARD_INTEGRATION.md           # Integration guidance
├── TECHNICAL_AUDIT_REPORT.md          # Initial audit report
├── FINAL_AUDIT_REPORT.md              # This final audit report
├── requirements.txt                   # Dependencies
├── inference.py                       # Inference pipeline
├── test_inference.py                  # Test suite (14 tests)
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

## Final Verdict Summary

| Component | Verdict | Status |
|-----------|---------|--------|
| Dataset | SYNTHETIC/DERIVED | Suitable for demo with clear limitations |
| Target | DERIVED (NOT OBSERVED) | Critical limitation - rule-learning |
| Leakage | NO LEAKAGE | Correctly implemented |
| Validation | CORRECT | Group-aware split, proper metrics |
| Model | APPROPRIATE | Sound architecture |
| Inference | PRODUCTION-READY | Robust validation and error handling |
| FarmGuard Integration | REQUIRES EXTENSION | Use defaults for demo, extend schema for production |
| Architecture | PYTHON SERVICE REQUIRED | Cannot run in Angular/Supabase directly |
| Test Suite | ALL PASSING | 14/14 tests passing |
| Repository | CLEAN | Minimal structure, no unnecessary files |

**Overall Assessment:** The model is suitable for hackathon demonstration as a prototype risk classifier, provided all limitations are clearly communicated. It is NOT suitable for production use without real-world validation and database schema extensions.

---

## Recommendations

### For Hackathon Demo
1. Deploy as separate Python inference service (FastAPI/Flask)
2. Use documented defaults for missing FarmGuard fields
3. Clearly communicate synthetic/derived nature in presentation
4. Use scientifically honest wording: "Prototype risk classifier"
5. Do NOT claim real-world predictive accuracy

### For Production Deployment
1. Collect real-world observational data with actual heat stress outcomes
2. Extend FarmGuard database schema to include missing animal and location fields
3. Add wind and solar radiation to weather data collection
4. Validate model on real farm data before production use
5. Implement temporal validation for robustness assessment
6. Consider species-specific models if accuracy requirements are high

### For Future Development
1. Explore alternative algorithms (XGBoost, CatBoost, Neural Networks)
2. Add ensemble methods for improved robustness
3. Develop region-specific models for different climate zones
4. Integrate with weather forecast APIs for predictive alerts
5. Create web interface for farmer-friendly access

---

**Audit Completed:** August 27, 2026  
**Status:** COMPLETE - Model ready for hackathon demonstration with documented limitations  
**Test Suite:** 14/14 tests passing  
**Repository:** Clean and minimal structure
