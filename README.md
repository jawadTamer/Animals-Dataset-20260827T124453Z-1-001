# FarmGuard Animal Heat-Risk Prediction Model

## Overview

**IMPORTANT:** This is a **PROTOTYPE/DEMO** model trained on **SYNTHETIC/DERIVED** risk labels. The target (risk_level) is derived from THI (Temperature-Humidity Index) thresholds based on peer-reviewed scientific literature, not from observed ground truth outcomes. The model learns to approximate the THI-based labeling rule.

This model provides heat-stress risk level predictions for livestock based on environmental conditions and animal characteristics. It is designed as a decision-support system for agricultural operations to help farmers proactively manage heat stress in their animals.

**Risk Levels:**
- **Low**: Minimal heat stress risk
- **Moderate**: Moderate heat stress risk
- **High**: High heat stress risk
- **Critical**: Severe heat stress risk

**DISCLAIMER:** This is a decision-support system, not a veterinary diagnostic system. Predictions should be used alongside professional veterinary judgment. Do not use for unsupported species or without validation on real farm data.

---

## Dataset Information

### Source
**Synthetic dataset** created for FarmGuard demonstration/hackathon purposes.

### Dataset Size
- **Total samples**: 10,000
- **Total animals**: 1,000
- **Total farms**: 10
- **Time period**: January 1, 2023 - December 30, 2023

### Animal Species Represented
- Cattle (36.3%)
- Goats (31.9%)
- Sheep (31.8%)

### Geographic Coverage
- 10 farms across different climate zones:
  - Mediterranean
  - Continental
  - Oceanic
  - Semi-arid
- Latitude range: 30° - 45°
- Longitude range: -10° - 40°
- Elevation range: 50m - 500m

### Features

#### Environmental Features
- `temperature_c`: Air temperature in Celsius
- `humidity_percent`: Relative humidity percentage
- `wind_speed_m_s`: Wind speed in meters per second
- `solar_radiation_w_m2`: Solar radiation in W/m²
- `latitude`: Farm latitude
- `longitude`: Farm longitude
- `elevation_m`: Farm elevation in meters
- `climate_zone`: Climate zone classification

#### Animal Features
- `species`: Animal species (cattle, sheep, goat)
- `breed`: Animal breed (5 breeds per species)
- `age_years`: Animal age in years
- `weight_kg`: Animal weight in kilograms
- `sex`: Animal sex (male/female)
- `physiological_stage`: Physiological stage (lactating, dry, pregnant, growing)
- `health_status`: Health status (healthy, minor_illness, recovering)

#### Temporal Features
- `date`: Measurement date
- `day_of_year`: Day of year (1-365)
- `month`: Month (1-12)
- `season`: Season (Winter, Spring, Summer, Fall)

#### Derived Features (used for labeling only, not in model)
- `thi`: Temperature-Humidity Index
- `hli`: Heat Load Index

### Target Variable
- `risk_level`: Heat-stress risk level (Low, Moderate, High, Critical)

### Target Definition (CRITICAL)
**Risk levels are SYNTHETIC/DERIVED from THI (Temperature-Humidity Index) thresholds.** This is NOT observed ground truth. The model is learning to approximate a deterministic rule, not predict real-world outcomes.

THI calculation: `THI = (1.8 * T + 32) - ((0.55 - 0.0055 * RH) * (1.8 * T - 26))`

Species-specific thresholds:

**Cattle:**
- Low: THI < 72
- Moderate: 72 ≤ THI < 79
- High: 79 ≤ THI < 84
- Critical: THI ≥ 84

**Sheep:**
- Low: THI < 75
- Moderate: 75 ≤ THI < 82
- High: 82 ≤ THI < 87
- Critical: THI ≥ 87

**Goats:**
- Low: THI < 74
- Moderate: 74 ≤ THI < 81
- High: 81 ≤ THI < 86
- Critical: THI ≥ 86

### Labeling Methodology
Labels are **synthetic/derived** based on scientifically established THI thresholds for different livestock species from peer-reviewed literature. These labels are NOT observed ground truth but are derived from environmental measurements. The model is essentially learning to approximate the THI-based classification rule with some added noise (10% random perturbation during generation).

---

## Model Architecture

### Algorithm
Random Forest Classifier

### Hyperparameters
- `n_estimators`: 200
- `max_depth`: 15
- `min_samples_split`: 10
- `min_samples_leaf`: 5
- `class_weight`: balanced
- `random_state`: 42
- `n_jobs`: -1

### Input Features
18 features total:
- 7 categorical (encoded)
- 11 numerical (scaled)

### Output
Risk level prediction with probability distribution across 4 classes.

---

## Validation Strategy

### Train-Test Split
- **Group-aware split** by animal_id to prevent data leakage
- Training animals: 800 (80%)
- Test animals: 200 (20%)
- Training samples: 7,899
- Test samples: 2,101

### Rationale
Group-aware splitting ensures that all measurements from the same animal are contained within either the training or test set, preventing the model from learning animal-specific patterns that would not generalize to new animals.

---

## Model Performance

**IMPORTANT:** These metrics are on synthetic/derived data and do NOT represent real-world performance. The model is learning to approximate a deterministic THI-based rule.

### Overall Metrics
- **Accuracy**: 88.05%
- **Macro F1**: 82.78%
- **Weighted F1**: 88.15%

### Per-Class Performance

| Risk Level | Precision | Recall | F1-Score | Support |
|------------|-----------|--------|----------|---------|
| Critical   | 0.94      | 0.90   | 0.92     | 263     |
| High       | 0.70      | 0.82   | 0.76     | 213     |
| Low        | 0.95      | 0.94   | 0.95     | 1,284   |
| Moderate   | 0.70      | 0.68   | 0.69     | 341     |

### Confusion Matrix
```
[[ 236   26    0    1]
 [  15  174    1   23]
 [   0    1 1207   76]
 [   0   46   62  233]]
```

### Key Findings
- **Critical risk recall**: 90% (excellent - rarely misses critical events)
- **Low risk precision**: 95% (excellent - rarely false alarms for low risk)
- **Moderate risk performance**: Lower (69% F1) - more challenging to distinguish
- **High risk recall**: 82% (good balance)

---

## Feature Importance

### Top 10 Most Important Features

| Rank | Feature | Importance |
|------|---------|------------|
| 1 | temperature_c | 45.8% |
| 2 | humidity_percent | 10.7% |
| 3 | day_of_year | 10.0% |
| 4 | month | 6.9% |
| 5 | season_encoded | 4.2% |
| 6 | weight_kg | 3.6% |
| 7 | solar_radiation_w_m2 | 3.3% |
| 8 | wind_speed_m_s | 3.3% |
| 9 | age_years | 3.1% |
| 10 | breed_encoded | 1.7% |

### Interpretation
- **Temperature** is the dominant factor (45.8% importance)
- **Humidity** is the second most important (10.7%)
- **Temporal features** (day_of_year, month, season) collectively account for ~21% importance
- **Animal characteristics** (weight, age, breed) have moderate importance
- **Wind and solar radiation** have smaller but meaningful contributions

---

## Class Imbalance

### Distribution
- Low: 6,150 samples (61.5%)
- Moderate: 1,575 samples (15.75%)
- Critical: 1,261 samples (12.61%)
- High: 1,014 samples (10.14%)

### Handling Strategy
- Used `class_weight='balanced'` in Random Forest
- Model performs well despite imbalance
- Critical risk recall remains high (90%)

---

## Known Limitations

### 1. Synthetic/Derived Target (CRITICAL)
**Limitation**: The target (risk_level) is SYNTHETICALLY DERIVED from THI thresholds, not observed ground truth.

**Impact**: 
- The model is learning to approximate a deterministic rule (THI-based classification)
- Performance metrics do NOT represent real-world predictive capability
- This is rule-learning, not outcome prediction
- Correlation between THI and risk_level is 0.80 (highly deterministic)

**Mitigation**: 
- Clearly communicate this as a prototype/demo model
- Do NOT claim "88% real-world heat-stress prediction accuracy"
- Use scientifically honest wording: "Prototype risk classifier trained on synthetic/derived labels"
- Validate on real farm data before any production use

### 2. Synthetic Data
**Limitation**: The dataset is synthetic, not real-world observational data.

**Impact**: 
- Model performance metrics may not reflect real-world performance
- Relationships between features may be oversimplified
- May not capture complex real-world interactions

**Mitigation**: 
- Model should be validated on real farm data before production deployment
- Consider this a demonstration/prototype model

### 2. Single Year of Data
**Limitation**: Data covers only one year (2023).

**Impact**:
- Cannot capture year-to-year climate variations
- May not generalize to different years with extreme weather events
- Limited seasonal diversity

**Mitigation**:
- Collect multi-year data for retraining
- Monitor performance across different years

### 3. Geographic Scope
**Limitation**: Farms are limited to 30°-45° latitude, -10° to 40° longitude.

**Impact**:
- Model may not generalize to tropical or polar regions
- Limited climate zone diversity
- May not perform well in extreme climates

**Mitigation**:
- Expand geographic coverage in training data
- Create region-specific models if needed

### 4. Species Coverage
**Limitation**: Only three species represented (cattle, sheep, goats).

**Impact**:
- Cannot predict for other livestock (pigs, poultry, buffalo, etc.)
- Breed diversity limited to 5 breeds per species

**Mitigation**:
- Clearly document species limitations
- Do not use for unsupported species
- Collect data for additional species if needed

### 5. Missing Environmental Features
**Limitation**: Some environmental features not included (precipitation, cloud cover, AQI).

**Impact**:
- May miss important environmental factors
- Limited to temperature, humidity, wind, solar radiation

**Mitigation**:
- Consider adding additional environmental sensors
- Monitor if missing features affect performance

### 6. No Temporal Validation
**Limitation**: Validation is animal-level, not temporal.

**Impact**:
- Cannot assess model's ability to predict future events
- May not capture temporal drift

**Mitigation**:
- Implement temporal validation in future versions
- Monitor model performance over time

### 7. Moderate Risk Performance
**Limitation**: Moderate risk class has lower performance (69% F1).

**Impact**:
- May misclassify moderate risk as low or high
- Could lead to inappropriate interventions

**Mitigation**:
- Consider merging moderate with adjacent classes
- Collect more moderate risk samples
- Adjust decision thresholds based on business requirements

---

## Production Deployment Requirements

### Dependencies
- Python 3.8+
- pandas
- numpy
- scikit-learn
- joblib

### Model Artifacts
- `animal_heat_risk_model.pkl`: Trained Random Forest model
- `feature_scaler.pkl`: StandardScaler for numerical features
- `label_encoders.pkl`: LabelEncoders for categorical features
- `target_encoder.pkl`: LabelEncoder for target variable
- `feature_columns.pkl`: List of feature columns

### Input Requirements
The model requires the following input fields:

**Required:**
- `species`: Animal species (cattle, sheep, goat)
- `breed`: Animal breed
- `age_years`: Animal age in years
- `weight_kg`: Animal weight in kg
- `sex`: Animal sex (male, female)
- `physiological_stage`: Physiological stage (lactating, dry, pregnant, growing)
- `health_status`: Health status (healthy, minor_illness, recovering)
- `latitude`: Farm latitude
- `longitude`: Farm longitude
- `elevation_m`: Farm elevation in meters
- `climate_zone`: Climate zone (Mediterranean, Continental, Oceanic, Semi-arid)
- `temperature_c`: Air temperature in Celsius
- `humidity_percent`: Relative humidity percentage
- `wind_speed_m_s`: Wind speed in m/s
- `solar_radiation_w_m2`: Solar radiation in W/m²

**Optional:**
- `date`: Measurement date (defaults to current date if not provided)

### Output Format
```json
{
  "risk_level": "Low|Moderate|High|Critical",
  "risk_score": 0.0,
  "confidence": 0.0,
  "probabilities": {
    "Low": 0.0,
    "Moderate": 0.0,
    "High": 0.0,
    "Critical": 0.0
  }
}
```

### API Integration
The `inference.py` script provides a Python class `AnimalHeatRiskPredictor` for easy integration:

```python
from inference import AnimalHeatRiskPredictor

# Initialize predictor
predictor = AnimalHeatRiskPredictor()

# Single prediction
result = predictor.predict({
    'species': 'cattle',
    'breed': 'Holstein',
    'temperature_c': 35.0,
    'humidity_percent': 70,
    # ... other required fields
})

# Batch prediction
results = predictor.predict_batch(dataframe)
```

---

## Production Safety

### Important Disclaimers

1. **Decision-Support System Only**
   - This model is a decision-support tool, not a veterinary diagnostic system
   - Does not provide medical diagnoses or guaranteed outcomes
   - Should be used alongside professional veterinary judgment

2. **No Medical Certainty**
   - Predictions are probabilistic, not deterministic
   - Does not replace professional animal health assessment
   - Should not be used as sole basis for critical decisions

3. **Heat-Stress Specific**
   - Model predicts heat-stress risk only
   - Does not predict other health issues or diseases
   - Should be integrated with broader animal health monitoring

4. **Synthetic Data Limitations**
   - Trained on synthetic data for demonstration
   - Must be validated on real farm data before production use
   - Performance may differ in real-world conditions

5. **Species Limitations**
   - Only trained on cattle, sheep, and goats
   - Do not use for other species without retraining
   - Breed diversity limited to training data

---

## Model Interpretability

### Key Drivers of Heat-Risk Predictions

Based on feature importance analysis:

1. **Temperature** (45.8%): Primary driver - higher temperatures increase risk
2. **Humidity** (10.7%): Secondary driver - high humidity exacerbates heat stress
3. **Temporal Factors** (21%): Season and day of year capture seasonal patterns
4. **Animal Characteristics** (8.4%): Weight, age, and breed influence susceptibility
5. **Other Environmental** (6.6%): Wind and solar radiation modify heat load

### Environmental vs Animal Factors
- Environmental factors (temperature, humidity, wind, solar, temporal): ~74%
- Animal factors (species, breed, age, weight, physiological stage): ~26%

This suggests that environmental conditions are the primary drivers of heat-stress risk, but animal characteristics play a meaningful role in modulating susceptibility.

---

## Future Improvements

### Data Collection
- Collect real-world observational data from partner farms
- Expand geographic coverage to include more climate zones
- Add more species and breeds
- Collect multi-year data for temporal diversity
- Add additional environmental sensors (precipitation, cloud cover, AQI)

### Model Development
- Experiment with other algorithms (XGBoost, CatBoost, Neural Networks)
- Implement temporal validation
- Add ensemble methods
- Develop species-specific models if needed
- Incorporate more sophisticated feature engineering

### Deployment
- Develop REST API for easy integration
- Create web interface for farmers
- Implement real-time monitoring dashboards
- Add alert system for critical risk levels
- Integrate with weather forecast APIs for predictive alerts

---

## Contact and Support

For questions about this model or to discuss deployment, please refer to the FarmGuard project team.

---

## Citation

If you use this model in your work, please cite:

```
FarmGuard Animal Heat-Risk Prediction Model
Version 1.0
Generated: August 27, 2026
Dataset: Synthetic demonstration dataset
```

---

## License

This model and associated documentation are provided for FarmGuard project use.

---

## Version History

- **v1.0** (August 27, 2026): Initial release with synthetic dataset
  - Random Forest model
  - 10,000 synthetic samples
  - 3 species, 10 farms
  - 88% accuracy, 83% macro F1
