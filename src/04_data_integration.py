import pandas as pd

lines = pd.read_csv('data/lines.csv')   
substations = pd.read_csv('data/substations.csv')
utilities = pd.read_csv('data/utilities.csv')
# 1. Convert all ID columns to strings to prevent data type mismatches
lines['Utility ID'] = lines['Utility ID'].astype(str)
lines['Source Substation ID'] = lines['Source Substation ID'].astype(str)
lines['Destination Substation ID'] = lines['Destination Substation ID'].astype(str)

substations['Substation ID'] = substations['Substation ID'].astype(str)
utilities['Utility ID'] = utilities['Utility ID'].astype(str)

# 2. Join Utilities onto Lines
masterDs = lines.merge(
    utilities,
    on='Utility ID',
    how='left'
)

masterDs=lines.merge(
    substations[['Substation ID', 'Region']], 
    left_on='Source Substation', 
    right_on='Substation ID', 
    how='left'
)
region_lookup = substations.set_index('Substation ID')['Region'].to_dict()

# Dictionary 2: Quick lookup of Substation Status by Substation ID
status_lookup = substations.set_index('Substation ID')['Status'].to_dict()

print(f"\n--- Lookup Dictionaries Created ---")
print(f"Region lookup sample: {list(region_lookup.items())[:2]}")
print(f"Status lookup sample: {list(status_lookup.items())[:2]}")


masterDs.to_csv('data/masterDataset.csv', index=False)
print("Master dataset successfully saved to 'data/masterDataset.csv")