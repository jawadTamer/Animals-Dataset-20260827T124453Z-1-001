import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

print("=" * 80)
print("CREATING SYNTHETIC FARMGUARD ANIMAL HEAT-RISK DATASET")
print("=" * 80)

# Configuration
n_samples = 10000
n_farms = 10
n_animals_per_farm = 100
date_start = datetime(2023, 1, 1)
date_end = datetime(2023, 12, 31)

# Farm locations (latitude, longitude, elevation)
farms = []
for i in range(n_farms):
    farms.append({
        'farm_id': f'FARM_{i+1:03d}',
        'latitude': np.random.uniform(30, 45),
        'longitude': np.random.uniform(-10, 40),
        'elevation_m': np.random.uniform(50, 500),
        'climate_zone': np.random.choice(['Mediterranean', 'Continental', 'Oceanic', 'Semi-arid'])
    })

farms_df = pd.DataFrame(farms)

# Animal species and breeds
species_config = {
    'cattle': {
        'breeds': ['Holstein', 'Jersey', 'Angus', 'Hereford', 'Simmental'],
        'weight_range': (400, 800),
        'age_range': (1, 10)
    },
    'sheep': {
        'breeds': ['Merino', 'Suffolk', 'Dorper', 'Texel', 'Rambouillet'],
        'weight_range': (50, 100),
        'age_range': (1, 8)
    },
    'goat': {
        'breeds': ['Alpine', 'Saanen', 'Boer', 'Nubian', 'Toggenburg'],
        'weight_range': (40, 80),
        'age_range': (1, 7)
    }
}

# Generate animals
animals = []
animal_id_counter = 1

for farm in farms:
    for _ in range(n_animals_per_farm):
        species = np.random.choice(list(species_config.keys()))
        config = species_config[species]
        
        animals.append({
            'animal_id': animal_id_counter,
            'farm_id': farm['farm_id'],
            'species': species,
            'breed': np.random.choice(config['breeds']),
            'age_years': np.random.uniform(*config['age_range']),
            'weight_kg': np.random.uniform(*config['weight_range']),
            'sex': np.random.choice(['male', 'female']),
            'physiological_stage': np.random.choice(['lactating', 'dry', 'pregnant', 'growing']),
            'health_status': np.random.choice(['healthy', 'minor_illness', 'recovering'], p=[0.9, 0.07, 0.03])
        })
        animal_id_counter += 1

animals_df = pd.DataFrame(animals)

# Generate environmental measurements and heat-stress labels
data = []

for _ in range(n_samples):
    # Random animal and farm
    animal = animals_df.sample(1).iloc[0]
    farm = farms_df[farms_df['farm_id'] == animal['farm_id']].iloc[0]
    
    # Random date
    days_diff = (date_end - date_start).days
    random_days = np.random.randint(0, days_diff)
    date = date_start + timedelta(days=random_days)
    
    # Seasonal temperature variation
    day_of_year = date.timetuple().tm_yday
    seasonal_temp = 20 + 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
    
    # Environmental measurements with realistic variation
    temperature_c = seasonal_temp + np.random.normal(0, 5)
    humidity_percent = np.clip(np.random.normal(60, 20), 10, 100)
    wind_speed_m_s = np.abs(np.random.normal(3, 2))
    solar_radiation_w_m2 = np.clip(np.random.normal(300, 150), 0, 1000)
    
    # Calculate THI (Temperature-Humidity Index)
    # THI = (1.8 * T + 32) - ((0.55 - 0.0055 * RH) * (1.8 * T - 26))
    T = temperature_c
    RH = humidity_percent
    thi = (1.8 * T + 32) - ((0.55 - 0.0055 * RH) * (1.8 * T - 26))
    
    # Calculate Heat Load Index (HLI) - more comprehensive
    # HLI = T + RH_adj + RAD_adj + WS_adj
    RH_adj = 0.5 * (RH - 60) / 100 * 10  # Simplified adjustment
    RAD_adj = solar_radiation_w_m2 / 200  # Simplified adjustment
    WS_adj = -wind_speed_m_s * 0.5  # Wind cooling effect
    hli = T + RH_adj + RAD_adj + WS_adj
    
    # Determine heat-stress risk level based on THI and species
    # Different thresholds for different species
    if animal['species'] == 'cattle':
        if thi < 72:
            risk_level = 'Low'
        elif thi < 79:
            risk_level = 'Moderate'
        elif thi < 84:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
    elif animal['species'] == 'sheep':
        if thi < 75:
            risk_level = 'Low'
        elif thi < 82:
            risk_level = 'Moderate'
        elif thi < 87:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
    else:  # goats
        if thi < 74:
            risk_level = 'Low'
        elif thi < 81:
            risk_level = 'Moderate'
        elif thi < 86:
            risk_level = 'High'
        else:
            risk_level = 'Critical'
    
    # Add some noise to make it more realistic (not perfect correlation)
    if np.random.random() < 0.1:  # 10% chance of different risk level
        levels = ['Low', 'Moderate', 'High', 'Critical']
        current_idx = levels.index(risk_level)
        new_idx = np.clip(current_idx + np.random.choice([-1, 1]), 0, 3)
        risk_level = levels[new_idx]
    
    data.append({
        'animal_id': animal['animal_id'],
        'farm_id': animal['farm_id'],
        'species': animal['species'],
        'breed': animal['breed'],
        'age_years': animal['age_years'],
        'weight_kg': animal['weight_kg'],
        'sex': animal['sex'],
        'physiological_stage': animal['physiological_stage'],
        'health_status': animal['health_status'],
        'latitude': farm['latitude'],
        'longitude': farm['longitude'],
        'elevation_m': farm['elevation_m'],
        'climate_zone': farm['climate_zone'],
        'date': date,
        'temperature_c': round(temperature_c, 2),
        'humidity_percent': round(humidity_percent, ),
        'wind_speed_m_s': round(wind_speed_m_s, 2),
        'solar_radiation_w_m2': round(solar_radiation_w_m2, 2),
        'thi': round(thi, 2),
        'hli': round(hli, 2),
        'risk_level': risk_level
    })

df = pd.DataFrame(data)

# Save datasets
animals_df.to_csv('c:/Users/jawad/Downloads/Animals Dataset-20260827T124453Z-1-001/farmguard_animals_metadata.csv', index=False)
farms_df.to_csv('c:/Users/jawad/Downloads/Animals Dataset-20260827T124453Z-1-001/farmguard_farms.csv', index=False)
df.to_csv('c:/Users/jawad/Downloads/Animals Dataset-20260827T124453Z-1-001/farmguard_animal_heat_risk.csv', index=False)

print("\nDataset created successfully!")
print(f"\nTotal samples: {len(df)}")
print(f"Total animals: {len(animals_df)}")
print(f"Total farms: {len(farms_df)}")
print(f"\nDate range: {df['date'].min()} to {df['date'].max()}")

print("\nRisk level distribution:")
print(df['risk_level'].value_counts())
print("\nPercentage distribution:")
print(df['risk_level'].value_counts(normalize=True) * 100)

print("\nSpecies distribution:")
print(df['species'].value_counts())

print("\nFeature columns:")
print(df.columns.tolist())

print("\nFiles saved:")
print("  - farmguard_animals_metadata.csv")
print("  - farmguard_farms.csv")
print("  - farmguard_animal_heat_risk.csv")
