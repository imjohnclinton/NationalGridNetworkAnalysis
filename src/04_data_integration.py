import pandas as pd

lines = pd.read_csv('data/lines.csv')   
substations = pd.read_csv('data/substations.csv')

lines['Source Substation'] = lines['Source Substation'].astype(str)
lines['Destination Substation'] = lines['Destination Substation'].astype(str)
substations['Substation ID'] = substations['Substation ID'].astype(str)


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