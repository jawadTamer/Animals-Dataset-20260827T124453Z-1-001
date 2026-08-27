# FarmGuard Animal Heat-Risk Prediction Model - Dataset Audit Report

**Date:** August 27, 2026  
**Dataset:** FarmGuard_Animals_Cleaned.xlsx  
**Status:** NOT READY FOR MODELING

---

## Executive Summary

After a comprehensive audit of the animal dataset, **the dataset is NOT suitable for building an animal heat-risk prediction model** as currently structured. The dataset appears to be from a controlled experimental study measuring physiological responses to different Temperature-Humidity Index (THI) conditions, rather than observational data suitable for predictive modeling.

**Critical Blocking Issue:** No legitimate target variable exists. The apparent target (`heat_stress_period`) is derived directly from `thi_range_code`, creating severe data leakage.

---

## STEP 1: Complete Dataset Audit

### Dataset Overview
- **File:** `FarmGuard_Animals_Cleaned.xlsx`
- **Rows:** 750
- **Columns:** 14
- **Unique Animals:** 50
- **Measurements per Animal:** 15 (5 replications × 3 THI conditions)

### Column Inventory

| Column | Data Type | Missing % | Unique Values | Description |
|--------|-----------|-----------|---------------|-------------|
| animal_id | int64 | 0.00% | 50 | Individual animal identifier |
| genetic_group | str | 0.00% | 5 | Genetic composition (Local, HF50, HF62.5, HF75, HF87.5) |
| thi_range_code | str | 0.00% | 3 | THI category (T0, T1, T2) |
| heat_stress_period | str | 0.00% | 3 | THI-based stress level (Low, Moderate, High) |
| replication_no | int64 | 0.00% | 5 | Replication number (1-5) |
| cortisol_ugdL | float64 | 0.00% | 447 | Cortisol level (stress hormone) |
| glucose_mmol_L | float64 | 0.00% | 106 | Glucose level |
| total_protein_gdL | float64 | 0.00% | 262 | Total protein |
| uric_acid_mgdL | float64 | 0.00% | 103 | Uric acid |
| cholesterol_mgdL | float64 | 0.00% | 734 | Cholesterol |
| calcium_mgdL | float64 | 0.00% | 307 | Calcium |
| hdl_mgdL | float64 | 0.00% | 712 | HDL cholesterol |
| ast_UI | float64 | 0.00% | 558 | AST enzyme |
| alt_UI | float64 | 0.00% | 548 | ALT enzyme |

### Data Quality Assessment

**Missing Values:** None (0% across all columns)  
**Duplicate Rows:** 0 complete duplicates  
**Duplicate animal_id + replication_no:** 500 (expected - each animal measured 5 times per THI condition)  
**Outliers:** Minimal (0-3 outliers per biomarker using IQR method)  
**Impossible Values:** None detected (no negative values in physiological measurements)

**Near-Constant Columns:**
- genetic_group: 5 unique values (0.7%)
- thi_range_code: 3 unique values (0.4%)
- heat_stress_period: 3 unique values (0.4%)
- replication_no: 5 unique values (0.7%)

---

## STEP 2: Critical Animal Identification Problem

### Finding
**Animal species/type is not available in the current data.**

### Investigation Results
- **animal_id:** Contains 50 unique identifiers (102-511), but no species information
- **genetic_group:** Contains 5 values (Local, HF50, HF62.5, HF75, HF87.5)
- **No lookup table** or metadata file exists in the repository
- **No documentation** confirms the meaning of genetic_group codes

### Interpretation (Not Confirmed)
The genetic_group codes suggest:
- **HF** likely = Holstein Friesian (dairy cattle breed)
- **Numbers** (50, 62.5, 75, 87.5) likely represent percentage of Holstein genetics
- **Local** likely represents indigenous/local cattle breed

**However:** This is an interpretation, not explicit data. No documentation confirms this.

### Conclusion
The dataset does not contain explicit animal species information. Only genetic_group codes are available, which require domain knowledge interpretation. The model cannot be generalized to other species without explicit species data.

---

## STEP 3: Feature Relevance for Heat Stress

### Environmental Features Available
✓ **thi_range_code** (T0, T1, T2) - THI categories  
✗ NO direct temperature readings  
✗ NO direct humidity readings  
✗ NO heat index calculations  
✗ NO wet bulb temperature  
✗ NO wind speed  
✗ NO solar radiation  
✗ NO precipitation  
✗ NO cloud cover  
✗ NO AQI  
✗ NO timestamps/dates  
✗ NO duration of heat exposure  

### Animal Features Available
✓ **genetic_group** (Local, HF50, HF62.5, HF75, HF87.5)  
✓ **animal_id** (individual identifier)  
✗ NO explicit animal species  
✗ NO breed information (beyond genetic_group codes)  
✗ NO age  
✗ NO sex  
✗ NO weight  
✗ NO physiological stage (lactation, pregnancy)  
✗ NO health status  
✗ NO production status  

### Farm/Location Features Available
✗ NO latitude/longitude  
✗ NO farm_id  
✗ NO zone_id  
✗ NO elevation  
✗ NO climate/location metadata  

### Physiological/Biomarker Features Available
✓ **cortisol_ugdL** (stress hormone - DIRECTLY related to heat stress)  
✓ glucose_mmol_L  
✓ total_protein_gdL  
✓ uric_acid_mgdL  
✓ cholesterol_mgdL  
✓ calcium_mgdL  
✓ hdl_mgdL  
✓ ast_UI  
✓ alt_UI  

---

## STEP 4: Target Variable Analysis

### Apparent Target: heat_stress_period
**Values:** Low (THI < 72), Moderate (THI 72-79), High (THI >= 80)  
**Distribution:** Perfectly balanced (250 each, 33.3% per class)

### Critical Finding: Data Leakage
The `heat_stress_period` column is **derived directly from `thi_range_code`**:

| thi_range_code | heat_stress_period |
|----------------|-------------------|
| T0 | Low (THI < 72) |
| T1 | Moderate (THI 72-79) |
| T2 | High (THI >= 80) |

**This is a perfect 1:1 mapping.** Using `heat_stress_period` as a target would be severe data leakage. The model would simply learn:
- T0 → Low
- T1 → Moderate  
- T2 → High

This is not a legitimate prediction task.

### Alternative Targets
No other obvious target variable exists in the dataset.

---

## STEP 5: Data Leakage Analysis

### Types of Leakage Identified

1. **Target Leakage:** `heat_stress_period` is derived from `thi_range_code`
2. **Temporal Leakage:** Not applicable (no timestamps)
3. **Group Leakage:** Risk exists if splitting randomly by row (same animal in train/test)

### Validation Strategy Required
If modeling were possible, would require:
- Group K-Fold by animal_id
- OR Leave-One-Group-Out by animal_id
- Ensure all measurements from the same animal stay in the same fold

---

## STEP 6: Model Approach Determination

### Species-Specific vs Universal Model
- Only ONE genetic group per animal
- genetic_group represents breed composition, NOT different species
- All animals appear to be cattle (based on genetic_group interpretation)

**Conclusion:** This is NOT a multi-species dataset. A single model with genetic_group as a categorical feature would be appropriate, but limited to the genetic groups represented.

---

## STEP 7: Feature Engineering Strategy

### Available Features for Modeling
**Input features:**
1. genetic_group (categorical - 5 levels)
2. thi_range_code (categorical - 3 levels)
3. Physiological biomarkers (continuous):
   - cortisol_ugdL
   - glucose_mmol_L
   - total_protein_gdL
   - uric_acid_mgdL
   - cholesterol_mgdL
   - calcium_mgdL
   - hdl_mgdL
   - ast_UI
   - alt_UI

**Problem:** What is the TARGET?
- heat_stress_period CANNOT be used (data leakage from thi_range_code)
- No other target variable exists
- The biomarkers (especially cortisol) are RESPONSES to heat stress
- Predicting biomarkers from THI categories is trivial and not useful for heat-risk prediction

---

## STEP 8: Missing Data Analysis

**Missing values:** None across all columns (0%)

**Conclusion:** The complete absence of missing data is unusual and suggests the data is from a controlled experiment with rigorous data collection protocols.

---

## STEP 9: Model Selection Considerations

### Dataset Characteristics
- Small dataset (750 rows)
- 50 animals with repeated measurements
- Categorical features (genetic_group, thi_range_code)
- Continuous physiological features
- **NO legitimate target variable identified**

### Model Options (IF a target existed)
- CatBoost (good for categorical features)
- Random Forest (robust, interpretable)
- XGBoost (requires encoding)
- Logistic Regression (baseline)

**However:** Without a legitimate target, no model can be trained.

---

## STEP 10: Class Imbalance Analysis

**IF heat_stress_period were the target:**
- Low (THI < 72): 250 (33.3%)
- Moderate (THI 72-79): 250 (33.3%)
- High (THI >= 80): 250 (33.3%)

Perfectly balanced - no imbalance issue. **BUT this target cannot be used due to data leakage.**

---

## STEP 11: Validation Strategy

### Dataset Structure
- 50 unique animals
- Each animal has 15 measurements (5 replications × 3 THI conditions)
- Repeated measures from same animals

### Appropriate Validation Strategy
- Group K-Fold by animal_id to prevent leakage
- OR Leave-One-Group-Out by animal_id
- Ensure all measurements from the same animal stay in the same fold

### Temporal Validation
- NOT applicable (no timestamps)

---

## STEP 12: Model Interpretability

### Feature Importance Methods
- SHAP values (model-agnostic)
- Permutation importance
- Tree-based feature importance

### Key Question
"What environmental/animal factors are driving heat-risk predictions?"

**Problem:** Without a legitimate target, interpretability cannot be assessed.

---

## DATASET READINESS ASSESSMENT

# DATASET READINESS: NOT READY

---

## Critical Blocking Issues

### 1. NO LEGITIMATE TARGET VARIABLE
- heat_stress_period is derived from thi_range_code (data leakage)
- No other target variable exists
- The dataset appears to be from a controlled experiment measuring physiological responses to different THI conditions
- This is EXPERIMENTAL DATA, not observational/prediction data

### 2. MISSING ENVIRONMENTAL FEATURES
- No raw temperature or humidity measurements
- Only aggregated THI categories (T0, T1, T2)
- Cannot predict heat risk from environmental conditions
- The model would need to predict THI category, which is already known

### 3. MISSING ANIMAL SPECIES INFORMATION
- Animal species is not explicitly available
- Only genetic_group codes (HF50, HF62.5, etc.)
- Requires interpretation (likely Holstein Friesian cattle)
- Cannot generalize to other species without explicit data

### 4. MISSING FARM/LOCATION CONTEXT
- No farm_id, zone_id, or geographic coordinates
- No elevation or climate information
- Cannot account for regional variations

### 5. MISSING TEMPORAL INFORMATION
- No timestamps or dates
- Cannot perform temporal validation
- Cannot model seasonal patterns

### 6. DATASET STRUCTURE
- Small dataset (750 rows, 50 animals)
- Controlled experimental design
- Not representative of real-world farm conditions
- Each animal measured under all 3 THI conditions
- This is a within-subjects experimental design

---

## What Data Is Missing to Make This Dataset Ready?

### 1. TARGET VARIABLE
Need observed heat-stress outcomes (not THI-derived):
- Veterinary diagnoses of heat stress
- Observed clinical signs
- Production losses due to heat
- Mortality events

**OR:** A scientifically justified rule for deriving labels from biomarkers (e.g., cortisol thresholds)

### 2. ENVIRONMENTAL DATA
- Raw temperature measurements (°C)
- Raw humidity measurements (%)
- Wind speed
- Solar radiation
- Timestamps for all measurements

### 3. ANIMAL METADATA
- Explicit animal species (cattle, sheep, etc.)
- Breed information
- Age, sex, weight
- Physiological stage (lactation, pregnancy)
- Health status

### 4. FARM/LOCATION DATA
- Farm identifiers
- Geographic coordinates
- Elevation
- Climate zone

---

## Alternative Approaches

### OPTION A: Use This Dataset for a Different Task
- Predict physiological biomarkers from THI and genetic_group
- This is a regression task, not classification
- Could predict cortisol levels as a proxy for stress
- **But this is NOT heat-risk prediction**

### OPTION B: Derive a Target from Biomarkers
- Use cortisol thresholds to define heat stress
- Requires scientific justification for thresholds
- Would be SYNTHETIC/DERIVED labels (not observed ground truth)
- Must clearly document this limitation

### OPTION C: Obtain Additional Data
- Merge with observational farm data
- Add actual heat-stress event labels
- Add environmental sensor data
- Add animal metadata

---

## Final Recommendation

**DO NOT train a heat-risk prediction model on this dataset as-is.**

The dataset is NOT suitable for the intended purpose because:
1. No legitimate target variable exists
2. The apparent target (heat_stress_period) is data leakage
3. Environmental data is aggregated, not raw measurements
4. Animal species is not explicitly available
5. The dataset is from a controlled experiment, not observational data

---

## To Proceed, One of the Following Is Needed:

1. **A different dataset** with observed heat-stress outcomes
2. **Scientifically justified biomarker thresholds** for label derivation
3. **Additional observational data** to merge with this experimental data

---

## Dataset Metadata

- **Source:** FarmGuard_Animals_Cleaned.xlsx
- **Size:** 750 rows × 14 columns
- **Animals:** 50 unique individuals
- **Animal Species:** Not explicitly available (genetic_group codes suggest dairy cattle)
- **Geographic Coverage:** Unknown (no location data)
- **Time Coverage:** Unknown (no timestamps)
- **Data Type:** Controlled experimental study
- **THI Conditions:** 3 levels (T0, T1, T2)
- **Genetic Groups:** 5 (Local, HF50, HF62.5, HF75, HF87.5)

---

## Contact

For questions about this audit or to discuss next steps, please refer to the FarmGuard project team.

---

**Report Generated:** August 27, 2026  
**Auditor:** ML Engineer - FarmGuard Project  
**Purpose:** Dataset readiness assessment for animal heat-risk prediction model
