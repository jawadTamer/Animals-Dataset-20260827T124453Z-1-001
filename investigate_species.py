import pandas as pd
import os

# Load the dataset
df = pd.read_excel('c:/Users/jawad/Downloads/Animals Dataset-20260827T124453Z-1-001/Animals Dataset/FarmGuard_Animals_Cleaned.xlsx')

print("=" * 80)
print("STEP 2: CRITICAL ANIMAL IDENTIFICATION PROBLEM - INVESTIGATION")
print("=" * 80)

print("\nSearching for species-related terms in all text columns:")
for col in df.select_dtypes(include=['object']).columns:
    print(f"\n{col}:")
    print(f"  Unique values: {list(df[col].unique())}")

print("\n" + "=" * 80)
print("ANALYSIS OF genetic_group CODES")
print("=" * 80)

print("\ngenetic_group values:", df['genetic_group'].unique())
print("\nDistribution:")
print(df['genetic_group'].value_counts())

print("\n" + "=" * 80)
print("INTERPRETATION OF genetic_group CODES")
print("=" * 80)

print("\nThe genetic_group codes suggest:")
print("  - 'HF' likely stands for 'Holstein Friesian' (a dairy cattle breed)")
print("  - Numbers (50, 62.5, 75, 87.5) likely represent percentage of Holstein genetics")
print("  - 'Local' likely represents indigenous/local cattle breed")
print("\nThis pattern is consistent with crossbreeding studies in dairy cattle.")

print("\n" + "=" * 80)
print("SEARCHING FOR ADDITIONAL FILES")
print("=" * 80)

base_dir = 'c:/Users/jawad/Downloads/Animals Dataset-20260827T124453Z-1-001'
for root, dirs, files in os.walk(base_dir):
    for file in files:
        file_path = os.path.join(root, file)
        print(f"\nFound: {file_path}")
        # Check file extension
        if file.endswith('.txt') or file.endswith('.csv') or file.endswith('.json'):
            print(f"  -> This might contain metadata")

print("\n" + "=" * 80)
print("CONCLUSION ON ANIMAL SPECIES")
print("=" * 80)

print("\nEXPLICIT species information is NOT available in the dataset.")
print("\nThe genetic_group codes (HF50, HF62.5, HF75, HF87.5, Local) strongly suggest:")
print("  - The animals are likely CATTLE (specifically dairy cattle)")
print("  - HF = Holstein Friesian crossbreeds")
print("  - Numbers represent genetic composition percentages")
print("\nHOWEVER:")
print("  - This is an INTERPRETATION, not explicit data")
print("  - No documentation confirms this interpretation")
print("  - No lookup table or metadata file exists")
print("\nTherefore:")
print("  'Animal species/type is not available in the current data.'")
print("  (Only genetic_group codes are available, which require interpretation)")
