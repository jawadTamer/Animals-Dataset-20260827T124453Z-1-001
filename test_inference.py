"""
Test suite for FarmGuard Animal Heat-Risk Prediction Model
"""
import sys
import pandas as pd
from inference import AnimalHeatRiskPredictor

def test_valid_cattle():
    """Test valid cattle input"""
    predictor = AnimalHeatRiskPredictor()
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
        'solar_radiation_w_m2': 400
    }
    result = predictor.predict(input_data)
    assert 'risk_level' in result
    assert 'risk_score' in result
    assert 'confidence' in result
    assert 'probabilities' in result
    assert result['risk_level'] in ['Low', 'Moderate', 'High', 'Critical']
    print("✓ Test valid cattle: PASSED")

def test_valid_sheep():
    """Test valid sheep input"""
    predictor = AnimalHeatRiskPredictor()
    input_data = {
        'species': 'sheep',
        'breed': 'Merino',
        'age_years': 3.0,
        'weight_kg': 70,
        'sex': 'female',
        'physiological_stage': 'lactating',
        'health_status': 'healthy',
        'latitude': 41.0,
        'longitude': -4.0,
        'elevation_m': 300,
        'climate_zone': 'Continental',
        'temperature_c': 25.0,
        'humidity_percent': 50,
        'wind_speed_m_s': 5.0,
        'solar_radiation_w_m2': 300
    }
    result = predictor.predict(input_data)
    assert result['risk_level'] in ['Low', 'Moderate', 'High', 'Critical']
    print("✓ Test valid sheep: PASSED")

def test_valid_goat():
    """Test valid goat input"""
    predictor = AnimalHeatRiskPredictor()
    input_data = {
        'species': 'goat',
        'breed': 'Alpine',
        'age_years': 2.5,
        'weight_kg': 55,
        'sex': 'male',
        'physiological_stage': 'growing',
        'health_status': 'healthy',
        'latitude': 35.0,
        'longitude': 10.0,
        'elevation_m': 250,
        'climate_zone': 'Mediterranean',
        'temperature_c': 30.0,
        'humidity_percent': 60,
        'wind_speed_m_s': 3.0,
        'solar_radiation_w_m2': 350
    }
    result = predictor.predict(input_data)
    assert result['risk_level'] in ['Low', 'Moderate', 'High', 'Critical']
    print("✓ Test valid goat: PASSED")

def test_missing_required_field():
    """Test missing required field"""
    predictor = AnimalHeatRiskPredictor()
    input_data = {
        'species': 'cattle',
        'breed': 'Holstein',
        # Missing age_years
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
        'solar_radiation_w_m2': 400
    }
    try:
        result = predictor.predict(input_data)
        print("✗ Test missing required field: FAILED (should raise ValueError)")
        sys.exit(1)
    except ValueError as e:
        assert 'Missing required fields' in str(e)
        print("✓ Test missing required field: PASSED")

def test_unseen_species():
    """Test unsupported species"""
    predictor = AnimalHeatRiskPredictor()
    input_data = {
        'species': 'chicken',
        'breed': 'Leghorn',
        'age_years': 1.0,
        'weight_kg': 2,
        'sex': 'female',
        'physiological_stage': 'growing',
        'health_status': 'healthy',
        'latitude': 40.5,
        'longitude': -3.7,
        'elevation_m': 200,
        'climate_zone': 'Mediterranean',
        'temperature_c': 35.0,
        'humidity_percent': 70,
        'wind_speed_m_s': 2.5,
        'solar_radiation_w_m2': 400
    }
    try:
        result = predictor.predict(input_data)
        print("✗ Test unseen species: FAILED (should raise ValueError)")
        sys.exit(1)
    except ValueError as e:
        assert 'Unsupported species' in str(e)
        print("✓ Test unseen species: PASSED")

def test_extreme_heat():
    """Test extreme heat conditions"""
    predictor = AnimalHeatRiskPredictor()
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
        'temperature_c': 45.0,
        'humidity_percent': 80,
        'wind_speed_m_s': 1.0,
        'solar_radiation_w_m2': 800
    }
    result = predictor.predict(input_data)
    # Extreme heat should result in High or Critical risk
    assert result['risk_level'] in ['High', 'Critical']
    print("✓ Test extreme heat: PASSED")

def test_normal_weather():
    """Test normal weather conditions"""
    predictor = AnimalHeatRiskPredictor()
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
        'temperature_c': 20.0,
        'humidity_percent': 50,
        'wind_speed_m_s': 5.0,
        'solar_radiation_w_m2': 200
    }
    result = predictor.predict(input_data)
    # Normal weather should result in Low or Moderate risk
    assert result['risk_level'] in ['Low', 'Moderate']
    print("✓ Test normal weather: PASSED")

def test_batch_prediction():
    """Test batch prediction"""
    predictor = AnimalHeatRiskPredictor()
    batch_input = pd.DataFrame([
        {
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
            'solar_radiation_w_m2': 400
        },
        {
            'species': 'sheep',
            'breed': 'Merino',
            'age_years': 3.0,
            'weight_kg': 70,
            'sex': 'female',
            'physiological_stage': 'lactating',
            'health_status': 'healthy',
            'latitude': 41.0,
            'longitude': -4.0,
            'elevation_m': 300,
            'climate_zone': 'Continental',
            'temperature_c': 25.0,
            'humidity_percent': 50,
            'wind_speed_m_s': 5.0,
            'solar_radiation_w_m2': 300
        }
    ])
    results = predictor.predict_batch(batch_input)
    assert len(results) == 2
    assert 'predicted_risk_level' in results.columns
    assert 'confidence' in results.columns
    print("✓ Test batch prediction: PASSED")

def test_output_schema():
    """Test output schema compliance"""
    predictor = AnimalHeatRiskPredictor()
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
        'solar_radiation_w_m2': 400
    }
    result = predictor.predict(input_data)
    
    # Check required fields
    required_fields = ['risk_level', 'risk_score', 'confidence', 'probabilities']
    for field in required_fields:
        assert field in result, f"Missing field: {field}"
    
    # Check risk_score is numeric and between 0-100
    assert isinstance(result['risk_score'], (int, float))
    assert 0 <= result['risk_score'] <= 100
    
    # Check confidence is between 0-1
    assert 0 <= result['confidence'] <= 1
    
    # Check probabilities sum to ~1
    prob_sum = sum(result['probabilities'].values())
    assert 0.99 <= prob_sum <= 1.01
    
    # Check all risk levels in probabilities
    for level in ['Low', 'Moderate', 'High', 'Critical']:
        assert level in result['probabilities']
    
    print("✓ Test output schema: PASSED")

if __name__ == "__main__":
    print("=" * 80)
    print("FARMGUARD ANIMAL HEAT-RISK MODEL - TEST SUITE")
    print("=" * 80)
    print()
    
    try:
        test_valid_cattle()
        test_valid_sheep()
        test_valid_goat()
        test_missing_required_field()
        test_unseen_species()
        test_extreme_heat()
        test_normal_weather()
        test_batch_prediction()
        test_output_schema()
        
        print()
        print("=" * 80)
        print("ALL TESTS PASSED")
        print("=" * 80)
    except Exception as e:
        print()
        print("=" * 80)
        print(f"TEST FAILED: {e}")
        print("=" * 80)
        sys.exit(1)
