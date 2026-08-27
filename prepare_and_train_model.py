import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GroupKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
import joblib
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("FARMGUARD ANIMAL HEAT-RISK PREDICTION MODEL")
print("=" * 80)

# Load dataset
df = pd.read_csv('data/farmguard_animal_heat_risk.csv')

print(f"\nDataset shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")

# Data cleaning and preparation
print("\n" + "=" * 80)
print("STEP 1: DATA CLEANING")
print("=" * 80)

# Check for missing values
print("\nMissing values:")
print(df.isnull().sum())

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])

# Extract temporal features
df['day_of_year'] = df['date'].dt.dayofyear
df['month'] = df['date'].dt.month
df['season'] = df['month'].apply(lambda x: 'Winter' if x in [12,1,2] else 'Spring' if x in [3,4,5] else 'Summer' if x in [6,7,8] else 'Fall')

print("\n" + "=" * 80)
print("STEP 2: FEATURE ENGINEERING")
print("=" * 80)

# Define features
categorical_features = ['species', 'breed', 'sex', 'physiological_stage', 'health_status', 'climate_zone', 'season']
numerical_features = ['age_years', 'weight_kg', 'latitude', 'longitude', 'elevation_m', 
                      'temperature_c', 'humidity_percent', 'wind_speed_m_s', 'solar_radiation_w_m2',
                      'day_of_year', 'month']
target = 'risk_level'

# Remove thi and hli from features (these are derived from environmental data)
features_to_use = categorical_features + numerical_features

print(f"\nFeatures to use: {len(features_to_use)}")
print(f"Categorical: {len(categorical_features)}")
print(f"Numerical: {len(numerical_features)}")

# Encode categorical features
label_encoders = {}
for col in categorical_features:
    le = LabelEncoder()
    df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
    label_encoders[col] = le

# Prepare feature matrix
feature_cols = [col + '_encoded' for col in categorical_features] + numerical_features
X = df[feature_cols]
y = df[target]

# Encode target
target_encoder = LabelEncoder()
y_encoded = target_encoder.fit_transform(y)

print(f"\nTarget classes: {target_encoder.classes_}")
print(f"Target distribution:")
print(pd.Series(y_encoded).value_counts())

print("\n" + "=" * 80)
print("STEP 3: TRAIN-TEST SPLIT")
print("=" * 80)

# Use group-aware split by animal_id to prevent leakage
animal_ids = df['animal_id'].values
unique_animals = np.unique(animal_ids)

# Split animals (not rows) to prevent leakage
train_animals, test_animals = train_test_split(unique_animals, test_size=0.2, random_state=42)

train_mask = df['animal_id'].isin(train_animals)
test_mask = df['animal_id'].isin(test_animals)

X_train = X[train_mask]
X_test = X[test_mask]
y_train = y_encoded[train_mask]
y_test = y_encoded[test_mask]

print(f"\nTraining samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")
print(f"Training animals: {len(train_animals)}")
print(f"Test animals: {len(test_animals)}")

print("\n" + "=" * 80)
print("STEP 4: MODEL TRAINING")
print("=" * 80)

# Scale numerical features
scaler = StandardScaler()
X_train_scaled = X_train.copy()
X_test_scaled = X_test.copy()

X_train_scaled[numerical_features] = scaler.fit_transform(X_train[numerical_features])
X_test_scaled[numerical_features] = scaler.transform(X_test[numerical_features])

# Train Random Forest model
print("\nTraining Random Forest model...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train_scaled, y_train)
print("Model trained successfully!")

print("\n" + "=" * 80)
print("STEP 5: MODEL EVALUATION")
print("=" * 80)

# Predictions
y_pred = rf_model.predict(X_test_scaled)
y_pred_proba = rf_model.predict_proba(X_test_scaled)

# Metrics
accuracy = accuracy_score(y_test, y_pred)
macro_f1 = f1_score(y_test, y_pred, average='macro')
weighted_f1 = f1_score(y_test, y_pred, average='weighted')

print(f"\nAccuracy: {accuracy:.4f}")
print(f"Macro F1: {macro_f1:.4f}")
print(f"Weighted F1: {weighted_f1:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_encoder.classes_))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Per-class metrics
print("\nPer-class metrics:")
for i, class_name in enumerate(target_encoder.classes_):
    class_mask = (y_test == i)
    if class_mask.sum() > 0:
        class_acc = accuracy_score(y_test[class_mask], y_pred[class_mask])
        class_f1 = f1_score(y_test[class_mask], y_pred[class_mask], average='micro')
        print(f"{class_name}: Accuracy={class_acc:.4f}, F1={class_f1:.4f}")

# Feature importance
print("\n" + "=" * 80)
print("STEP 6: FEATURE IMPORTANCE")
print("=" * 80)

feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 10 most important features:")
print(feature_importance.head(10))

print("\n" + "=" * 80)
print("STEP 7: SAVE MODEL ARTIFACTS")
print("=" * 80)

# Save model and preprocessing objects
joblib.dump(rf_model, 'model/animal_heat_risk_model.pkl')
joblib.dump(scaler, 'model/feature_scaler.pkl')
joblib.dump(label_encoders, 'model/label_encoders.pkl')
joblib.dump(target_encoder, 'model/target_encoder.pkl')
joblib.dump(feature_cols, 'model/feature_columns.pkl')

print("\nModel artifacts saved:")
print("  - model/animal_heat_risk_model.pkl")
print("  - model/feature_scaler.pkl")
print("  - model/label_encoders.pkl")
print("  - model/target_encoder.pkl")
print("  - model/feature_columns.pkl")

print("\n" + "=" * 80)
print("TRAINING COMPLETE")
print("=" * 80)
