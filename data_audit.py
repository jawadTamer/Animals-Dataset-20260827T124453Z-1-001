import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_excel('c:/Users/jawad/Downloads/Animals Dataset-20260827T124453Z-1-001/Animals Dataset/FarmGuard_Animals_Cleaned.xlsx')

print("=" * 80)
print("STEP 1: COMPLETE DATASET AUDIT")
print("=" * 80)

print("\n1. Number of rows:", df.shape[0])
print("2. Number of columns:", df.shape[1])

print("\n3. Column names:")
for i, col in enumerate(df.columns, 1):
    print(f"   {i}. {col}")

print("\n4. Data types:")
print(df.dtypes)

print("\n5. Missing-value percentage for every column:")
missing_pct = (df.isnull().sum() / len(df)) * 100
for col in df.columns:
    print(f"   {col}: {missing_pct[col]:.2f}%")

print("\n6. Number of unique values:")
for col in df.columns:
    unique_count = df[col].nunique()
    unique_pct = unique_count / len(df) * 100
    print(f"   {col}: {unique_count} unique values ({unique_pct:.1f}%)")

print("\n7. Example values (first 3 rows):")
print(df.head(3))

print("\n8. Duplicate rows:")
print(f"   Full duplicate rows: {df.duplicated().sum()}")
print(f"   Duplicate animal_id + replication_no: {df.duplicated(subset=['animal_id', 'replication_no']).sum()}")

print("\n9. Constant / near-constant columns:")
for col in df.columns:
    unique_count = df[col].nunique()
    unique_pct = unique_count / len(df) * 100
    if unique_pct < 5:
        print(f"   {col}: {unique_count} unique values ({unique_pct:.1f}%) - NEAR-CONSTANT")

print("\n10. Checking for outliers using IQR method:")
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)].shape[0]
    print(f"   {col}: {outliers} outliers ({outliers/len(df)*100:.1f}%)")

print("\n11. Checking for impossible values:")
print("   cortisol_ugdL - checking for negative values:", (df['cortisol_ugdL'] < 0).sum())
print("   glucose_mmol_L - checking for negative values:", (df['glucose_mmol_L'] < 0).sum())
print("   cholesterol_mgdL - checking for negative values:", (df['cholesterol_mgdL'] < 0).sum())

print("\n12. Class distribution for heat_stress_period (potential target):")
print(df['heat_stress_period'].value_counts())
print("\nPercentage distribution:")
print(df['heat_stress_period'].value_counts(normalize=True) * 100)

print("\n" + "=" * 80)
print("STEP 2: CRITICAL ANIMAL IDENTIFICATION PROBLEM")
print("=" * 80)

print("\nUnique animal_id count:", df['animal_id'].nunique())
print("\nAnimal ID range:", df['animal_id'].min(), "to", df['animal_id'].max())
print("\nRecords per animal_id (first 10):")
print(df['animal_id'].value_counts().head(10))

print("\nUnique genetic_group values:", df['genetic_group'].unique())
print("\nGenetic group distribution:")
print(df['genetic_group'].value_counts())

print("\n" + "=" * 80)
print("STEP 3: FEATURE RELEVANCE FOR HEAT STRESS")
print("=" * 80)

print("\nEnvironmental features available:")
print("   - thi_range_code (Temperature-Humidity Index categories: T0, T1, T2)")
print("   - heat_stress_period (THI-based categories: Low, Moderate, High)")

print("\nAnimal features available:")
print("   - genetic_group (Local, HF50, HF62.5, HF75, HF87.5)")
print("   - animal_id (individual identifier)")

print("\nPhysiological/blood biomarker features available:")
print("   - cortisol_ugdL (stress hormone)")
print("   - glucose_mmol_L")
print("   - total_protein_gdL")
print("   - uric_acid_mgdL")
print("   - cholesterol_mgdL")
print("   - calcium_mgdL")
print("   - hdl_mgdL")
print("   - ast_UI")
print("   - alt_UI")

print("\nMissing environmental features:")
print("   - NO direct temperature readings")
print("   - NO direct humidity readings")
print("   - NO wind speed")
print("   - NO solar radiation")
print("   - NO precipitation")
print("   - NO timestamps/dates")
print("   - NO location/farm coordinates")
print("   - NO elevation")

print("\nMissing animal features:")
print("   - NO explicit animal species (cattle, sheep, etc.)")
print("   - NO breed information")
print("   - NO age")
print("   - NO sex")
print("   - NO weight")
print("   - NO physiological stage (lactation, pregnancy)")
print("   - NO health status")

print("\n" + "=" * 80)
print("STEP 4: TARGET VARIABLE ANALYSIS")
print("=" * 80)

print("\nPotential target: heat_stress_period")
print("Values:", df['heat_stress_period'].unique())
print("\nDistribution:")
print(df['heat_stress_period'].value_counts())
print("\nThis appears to be derived from THI (Temperature-Humidity Index)")
print("THI ranges:")
print("   - Low: THI < 72")
print("   - Moderate: THI 72-79")
print("   - High: THI >= 80")

print("\n" + "=" * 80)
print("STEP 5: DATA LEAKAGE CHECK")
print("=" * 80)

print("\nCRITICAL FINDING: heat_stress_period is derived from THI")
print("thi_range_code mapping:")
print(pd.crosstab(df['thi_range_code'], df['heat_stress_period']))
print("\nT0 -> Low (THI < 72)")
print("T1 -> Moderate (THI 72-79)")
print("T2 -> High (THI >= 80)")
print("\nThis is a PERFECT mapping - thi_range_code directly determines heat_stress_period")
print("Using heat_stress_period as a target would be SEVERE DATA LEAKAGE")

print("\n" + "=" * 80)
print("SUMMARY OF CRITICAL ISSUES")
print("=" * 80)
print("\n1. Animal species is NOT explicitly available (only genetic_group codes)")
print("2. Environmental data is aggregated (THI categories only, no raw measurements)")
print("3. heat_stress_period is derived from thi_range_code - CANNOT be used as target")
print("4. No timestamps, location data, or farm information")
print("5. Dataset appears to be from a controlled experiment with 50 animals")
print("6. Each animal has 15 measurements (5 replications × 3 THI conditions)")
