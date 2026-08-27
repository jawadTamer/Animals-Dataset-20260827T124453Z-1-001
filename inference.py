import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class AnimalHeatRiskPredictor:
    """
    FarmGuard Animal Heat-Risk Prediction Model
    
    This is a PROTOTYPE/DEMO model trained on synthetic/derived risk labels.
    The target (risk_level) is derived from THI (Temperature-Humidity Index) thresholds,
    not observed ground truth. The model learns to approximate the THI-based labeling rule.
    
    Supported species: cattle, sheep, goats only.
    
    Risk Levels:
    - Low: Minimal heat stress risk
    - Moderate: Moderate heat stress risk
    - High: High heat stress risk
    - Critical: Severe heat stress risk
    
    IMPORTANT: This is a decision-support system, not a veterinary diagnostic system.
    """
    
    def __init__(self, model_path='model/animal_heat_risk_model.pkl',
                 scaler_path='model/feature_scaler.pkl',
                 label_encoders_path='model/label_encoders.pkl',
                 target_encoder_path='model/target_encoder.pkl',
                 feature_columns_path='model/feature_columns.pkl'):
        """
        Load the trained model and preprocessing objects.
        
        Args:
            model_path: Path to trained model file
            scaler_path: Path to feature scaler file
            label_encoders_path: Path to label encoders file
            target_encoder_path: Path to target encoder file
            feature_columns_path: Path to feature columns file
        """
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.label_encoders = joblib.load(label_encoders_path)
        self.target_encoder = joblib.load(target_encoder_path)
        self.feature_columns = joblib.load(feature_columns_path)
        
        # Define numerical and categorical features
        self.categorical_features = ['species', 'breed', 'sex', 'physiological_stage', 
                                      'health_status', 'climate_zone', 'season']
        self.numerical_features = ['age_years', 'weight_kg', 'latitude', 'longitude', 
                                     'elevation_m', 'temperature_c', 'humidity_percent', 
                                     'wind_speed_m_s', 'solar_radiation_w_m2', 
                                     'day_of_year', 'month']
        
        # Supported species
        self.supported_species = ['cattle', 'sheep', 'goat']
        
        # Required fields for prediction
        self.required_fields = ['species', 'breed', 'age_years', 'weight_kg', 'sex',
                               'physiological_stage', 'health_status', 'latitude',
                               'longitude', 'elevation_m', 'climate_zone',
                               'temperature_c', 'humidity_percent', 'wind_speed_m_s',
                               'solar_radiation_w_m2']
    
    def validate_input(self, input_data):
        """
        Validate input data.
        
        Args:
            input_data: Dictionary containing input features
            
        Raises:
            ValueError: If validation fails
        """
        # Check species support
        if 'species' in input_data:
            if input_data['species'].lower() not in self.supported_species:
                raise ValueError(
                    f"Unsupported species '{input_data['species']}'. "
                    f"Supported species: {self.supported_species}"
                )
        
        # Check required fields
        missing_fields = [f for f in self.required_fields if f not in input_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Check for None values in required fields
        null_fields = [f for f in self.required_fields if input_data.get(f) is None]
        if null_fields:
            raise ValueError(f"Null values in required fields: {null_fields}")
    
    def preprocess_input(self, input_data):
        """
        Preprocess input data for prediction.
        
        Args:
            input_data: Dictionary or DataFrame containing input features
            
        Returns:
            Preprocessed feature matrix
        """
        if isinstance(input_data, dict):
            df = pd.DataFrame([input_data])
        else:
            df = input_data.copy()
        
        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df['day_of_year'] = df['date'].dt.dayofyear
            df['month'] = df['date'].dt.month
            df['season'] = df['month'].apply(
                lambda x: 'Winter' if x in [12,1,2] else 
                          'Spring' if x in [3,4,5] else 
                          'Summer' if x in [6,7,8] else 'Fall'
            )
        else:
            # If no date provided, use current date
            now = datetime.now()
            df['day_of_year'] = now.timetuple().tm_yday
            df['month'] = now.month
            df['season'] = 'Winter' if now.month in [12,1,2] else \
                          'Spring' if now.month in [3,4,5] else \
                          'Summer' if now.month in [6,7,8] else 'Fall'
        
        # Encode categorical features
        for col in self.categorical_features:
            if col in df.columns:
                if col in self.label_encoders:
                    # Handle unseen categories
                    le = self.label_encoders[col]
                    df[col + '_encoded'] = df[col].apply(
                        lambda x: le.transform([x])[0] if x in le.classes_ else -1
                    )
                else:
                    df[col + '_encoded'] = 0
            else:
                df[col + '_encoded'] = 0
        
        # Prepare feature matrix
        feature_cols = [col + '_encoded' for col in self.categorical_features] + self.numerical_features
        X = df[feature_cols]
        
        # Scale numerical features
        X_scaled = X.copy()
        X_scaled[self.numerical_features] = self.scaler.transform(X[self.numerical_features])
        
        return X_scaled
    
    def predict(self, input_data):
        """
        Predict heat-stress risk level.
        
        Args:
            input_data: Dictionary containing input features
            
        Returns:
            Dictionary with prediction results
            
        Raises:
            ValueError: If input validation fails
        """
        # Validate input
        if isinstance(input_data, dict):
            self.validate_input(input_data)
        
        # Preprocess
        X = self.preprocess_input(input_data)
        
        # Predict
        prediction_encoded = self.model.predict(X)[0]
        prediction_proba = self.model.predict_proba(X)[0]
        
        # Decode prediction
        risk_level = self.target_encoder.inverse_transform([prediction_encoded])[0]
        
        # Create probability dictionary
        prob_dict = {
            class_name: float(prob) 
            for class_name, prob in zip(self.target_encoder.classes_, prediction_proba)
        }
        
        # Calculate confidence (max probability)
        confidence = float(max(prediction_proba))
        
        # Calculate meaningful risk_score from probabilities
        # risk_score = weighted average where Low=0, Moderate=33.3, High=66.7, Critical=100
        risk_weights = {class_name: i * 33.33 for i, class_name in enumerate(self.target_encoder.classes_)}
        risk_score = sum(prob * risk_weights[class_name] for class_name, prob in prob_dict.items())
        
        return {
            'risk_level': risk_level,
            'risk_score': round(risk_score, 2),
            'confidence': round(confidence, 4),
            'probabilities': {k: round(v, 4) for k, v in prob_dict.items()}
        }
    
    def predict_batch(self, input_data):
        """
        Predict heat-stress risk for multiple animals.
        
        Args:
            input_data: DataFrame containing input features for multiple animals
            
        Returns:
            DataFrame with prediction results
        """
        # Preprocess
        X = self.preprocess_input(input_data)
        
        # Predict
        predictions_encoded = self.model.predict(X)
        predictions_proba = self.model.predict_proba(X)
        
        # Decode predictions
        risk_levels = self.target_encoder.inverse_transform(predictions_encoded)
        
        # Create results DataFrame
        results = input_data.copy()
        results['predicted_risk_level'] = risk_levels
        results['confidence'] = np.max(predictions_proba, axis=1)
        
        # Add probability columns
        for i, class_name in enumerate(self.target_encoder.classes_):
            results[f'prob_{class_name}'] = predictions_proba[:, i]
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize predictor with relative paths
    predictor = AnimalHeatRiskPredictor(
        model_path='model/animal_heat_risk_model.pkl',
        scaler_path='model/feature_scaler.pkl',
        label_encoders_path='model/label_encoders.pkl',
        target_encoder_path='model/target_encoder.pkl',
        feature_columns_path='model/feature_columns.pkl'
    )
    
    # Example single prediction
    print("=" * 80)
    print("EXAMPLE 1: Single Prediction")
    print("=" * 80)
    
    sample_input = {
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
    
    result = predictor.predict(sample_input)
    print("\nInput:")
    for key, value in sample_input.items():
        print(f"  {key}: {value}")
    
    print("\nPrediction:")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Confidence: {result['confidence']:.4f}")
    print(f"  Probabilities:")
    for level, prob in result['probabilities'].items():
        print(f"    {level}: {prob:.4f}")
    
    # Example batch prediction
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Batch Prediction")
    print("=" * 80)
    
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
            'solar_radiation_w_m2': 400,
            'date': '2023-07-15'
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
            'solar_radiation_w_m2': 300,
            'date': '2023-07-15'
        }
    ])
    
    batch_results = predictor.predict_batch(batch_input)
    print("\nBatch Predictions:")
    print(batch_results[['species', 'breed', 'temperature_c', 'humidity_percent', 
                         'predicted_risk_level', 'confidence']].to_string(index=False))
