import pandas as pd

utilities=pd.read_csv("data/utilities.csv")
substations=pd.read_csv("data/substations.csv")
lines=pd.read_csv("data/lines.csv")

# Step 2: Handle missing values
# Even though the generator produces clean data, treat this step seriously —
# real grid asset registers always have gaps. Decide on imputation strategies
# for different columns and document your decisions and rationale.



# Step 3: Data validation
# Verify every Source/Destination Substation ID in lines.csv exists in substations.csv
checkValS=set(substations['Substation ID'])
checkValU=set(utilities['Utility ID'])

invalidSources = lines[~lines['Source Substation ID'].isin(checkValS)]
invalidDestinations = lines[~lines['Destination Substation ID'].isin(checkValS)]
invalidUtilites=lines[~lines['Utility ID'].isin(checkValU)]

print(f"Missing Source Substations: {len(invalidSources)}")
print(f"missing Destination Substations: {len(invalidDestinations)}")
print(f"Lines with Invalid Utility IDs: {len(invalidUtilites)}")
print(f"----------------------------------------")

# Ensure data type consistency (numeric columns are truly numeric)

substations['Latitude'] = pd.to_numeric(substations['Latitude'], errors='coerce')
substations['Longitude'] = pd.to_numeric(substations['Longitude'], errors='coerce')
substations['Capacity (MVA)'] = pd.to_numeric(substations['Capacity (MVA)'], errors='coerce')
lines['Length (km)'] = pd.to_numeric(lines['Length (km)'], errors='coerce')


# Validate that latitude/longitude fall within plausible West African bounds
invalidLats = substations[(substations['Latitude'] < 4.5) | (substations['Latitude'] > 11.5)]
invalidLongs = substations[(substations['Longitude'] < -4.5) | (substations['Longitude'] > 3.0)]

print(f"Substations with out-of-bounds Latitude: {len(invalidLats)}")
print(f"Substations with out-of-bounds Longitude: {len(invalidLongs)}")
print(f"----------------------------------------")

# Check for duplicate entries
 
print(f"Duplicate Rows in Utilities:{utilities.duplicated().sum()}")
print(f"Duplicate Rows in Substations:{substations.duplicated().sum()}")
print(f"Duplicate Rows in lines:{lines.duplicated().sum()}")

utilities=utilities.drop_duplicates()
substations=substations.drop_duplicates()
lines=lines.drop_duplicates()

# Step 2: Handle missing values
print("Missing Values in Utilities:")
print(utilities.isnull().sum(), "\n")
print("Missing Values in Substations:")
print(substations.isnull().sum(), "\n")
print("Missing Values in Lines:")
print(lines.isnull().sum(), "\n")
print("----------------------------------------")