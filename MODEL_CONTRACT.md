# FarmGuard Animal Heat-Risk Model - Prediction Contract

## Model Identity

**Model Name:** FarmGuard Animal Heat-Risk Prediction Model  
**Model Type:** Prototype/Demo Risk Classifier  
**Algorithm:** Random Forest Classifier  
**Version:** 1.0  
**Date:** August 27, 2026  

**IMPORTANT DISCLAIMER:** This is a PROTOTYPE/DEMO model trained on SYNTHETIC/DERIVED risk labels. The target (risk_level) is derived from THI (Temperature-Humidity Index) thresholds, not observed ground truth. The model learns to approximate the THI-based labeling rule. This is a decision-support system, not a veterinary diagnostic system.

## Supported Species

**Supported:** cattle, sheep, goats  
**Unsupported:** chicken, pig, horse, buffalo, camel, duck, turkey, rabbit, and all other species

**Supported Breeds:**
- Cattle: Holstein, Jersey, Angus, Hereford, Simmental
- Sheep: Merino, Suffolk, Dorper, Texel, Rambouillet
- Goats: Alpine, Saanen, Boer, Nubian, Toggenburg

## Input Schema

### Required Fields

All of the following fields are REQUIRED for prediction:

```json
{
  "species": "cattle|sheep|goat",
  "breed": "string (must be from supported breeds)",
  "age_years": "number (0-15)",
  "weight_kg": "number (30-1000)",
  "sex": "male|female",
  "physiological_stage": "lactating|dry|pregnant|growing",
  "health_status": "healthy|minor_illness|recovering",
  "latitude": "number (-90 to 90)",
  "longitude": "number (-180 to 180)",
  "elevation_m": "number (0-5000)",
  "climate_zone": "Mediterranean|Continental|Oceanic|Semi-arid",
  "temperature_c": "number (-20 to 60)",
  "humidity_percent": "number (0-100)",
  "wind_speed_m_s": "number (0-30)",
  "solar_radiation_w_m2": "number (0-1500)"
}
```

### Optional Fields

```json
{
  "date": "string (ISO 8601 date format, e.g., '2023-07-15')"
}
```

If `date` is not provided, the current date is used.

## Input Validation

The model will **reject** predictions with `ValueError` if:

1. Species is not in the supported list (cattle, sheep, goat)
2. Any required field is missing
3. Any required field has a null value

## Output Schema

```json
{
  "risk_level": "Low|Moderate|High|Critical",
  "risk_score": "number (0-100)",
  "confidence": "number (0-1)",
  "probabilities": {
    "Low": "number (0-1)",
    "Moderate": "number (0-1)",
    "High": "number (0-1)",
    "Critical": "number (0-1)"
  }
}
```

## Output Field Definitions

### risk_level
The predicted heat-stress risk level:
- **Low**: Minimal heat stress risk
- **Moderate**: Moderate heat stress risk
- **High**: High heat stress risk
- **Critical**: Severe heat stress risk

### risk_score
A continuous risk score from 0 to 100, calculated as a weighted average of class probabilities:

```
risk_score = (Low_probability * 0) + (Moderate_probability * 33.33) + (High_probability * 66.67) + (Critical_probability * 100)
```

This provides a continuous measure of risk intensity, where:
- 0 = Definitely Low risk
- 33.33 = Definitely Moderate risk
- 66.67 = Definitely High risk
- 100 = Definitely Critical risk

Values between these represent uncertainty or mixed probabilities.

### confidence
The maximum probability across all classes (0 to 1). Higher values indicate more confident predictions.

### probabilities
The probability distribution across all four risk levels. These always sum to approximately 1.0.

## Example Usage

### Python

```python
from inference import AnimalHeatRiskPredictor

# Initialize predictor
predictor = AnimalHeatRiskPredictor()

# Single prediction
input_data = {
    'species': 'cattle',
    'breed': 'Holstein',
    'age_years': 4.5,
    'weight_kg': 600,
    'sex': 'female',
    'physiological_stage': 'lactating',
    'health_status': 'healthy',
    'latitude': 40.5,
    'longitude': -3.7,
    'elevation_m': 200,
    'climate_zone': 'Mediterranean',
    'temperature_c': 35.0,
    'humidity_percent': 70,
    'wind_speed_m_s': 2.5,
    'solar_radiation_w_m2': 400,
    'date': '2023-07-15'
}

result = predictor.predict(input_data)
print(result)
```

### Expected Output

```json
{
  "risk_level": "High",
  "risk_score": 72.45,
  "confidence": 0.8523,
  "probabilities": {
    "Low": 0.0234,
    "Moderate": 0.1243,
    "High": 0.8523,
    "Critical": 0.0000
  }
}
```

## Batch Prediction

For batch predictions, provide a pandas DataFrame with the same schema:

```python
import pandas as pd

batch_input = pd.DataFrame([
    { ... animal 1 data ... },
    { ... animal 2 data ... },
    { ... animal 3 data ... }
])

results = predictor.predict_batch(batch_input)
```

The output DataFrame includes all input columns plus:
- `predicted_risk_level`: The predicted risk level
- `confidence`: Prediction confidence
- `prob_Low`, `prob_Moderate`, `prob_High`, `prob_Critical`: Individual probabilities

## Error Handling

### Unsupported Species Error

```python
ValueError: Unsupported species 'chicken'. Supported species: ['cattle', 'sheep', 'goat']
```

### Missing Required Field Error

```python
ValueError: Missing required fields: ['age_years', 'weight_kg']
```

### Null Value Error

```python
ValueError: Null values in required fields: ['temperature_c']
```

## Model Artifacts

The following files are required for inference:

- `animal_heat_risk_model.pkl`: Trained Random Forest model
- `feature_scaler.pkl`: StandardScaler for numerical features
- `label_encoders.pkl`: LabelEncoders for categorical features
- `target_encoder.pkl`: LabelEncoder for target variable
- `feature_columns.pkl`: List of feature columns

## Dependencies

- Python 3.8+
- pandas >= 1.5.0
- numpy >= 1.23.0
- scikit-learn >= 1.2.0
- joblib >= 1.2.0

See `requirements.txt` for exact versions.

## Performance Metrics (Training)

**Note:** These metrics are on synthetic/derived data and may not reflect real-world performance.

- **Accuracy:** 88.05%
- **Macro F1:** 82.78%
- **Weighted F1:** 88.15%

**Per-Class Performance:**
- Critical: Precision=0.94, Recall=0.90, F1=0.92
- High: Precision=0.70, Recall=0.82, F1=0.76
- Low: Precision=0.95, Recall=0.94, F1=0.95
- Moderate: Precision=0.70, Recall=0.68, F1=0.69

## Limitations

1. **Synthetic Data:** Model is trained on synthetic data, not real-world observations
2. **Derived Target:** Risk labels are derived from THI thresholds, not observed outcomes
3. **Single Year:** Data covers only 2023, no year-to-year variation
4. **Geographic Scope:** Limited to 30°-45° latitude, -10° to 40° longitude
5. **Species Limitation:** Only supports cattle, sheep, goats
6. **Breed Limitation:** Only 5 breeds per species
7. **No Temporal Validation:** No temporal split implemented in training

## Integration with FarmGuard

See `FARMGUARD_INTEGRATION.md` for detailed integration guidance, including:
- Field mapping between FarmGuard database and model inputs
- Recommended defaults for missing fields
- Weather integration architecture
- Example integration code

## Safety and Responsibility

- This model is for decision-support only, not medical diagnosis
- Predictions should be used alongside professional veterinary judgment
- Do not use for unsupported species
- Validate on real farm data before production deployment
- Monitor performance over time

## Contact

For questions about this model or integration, refer to the FarmGuard project team.
