# Step 1: Load and examine raw data
import pandas as pd
import numpy as np
 
utilities = pd.read_csv('utilities.csv')
substations = pd.read_csv('substations.csv')
lines = pd.read_csv('lines.csv')
 
# Step 2: Handle missing values
# Even though the generator produces clean data, treat this step seriously —
# real grid asset registers always have gaps. Decide on imputation strategies
# for different columns and document your decisions and rationale.
 
# Step 3: Data validation
# Verify every Source/Destination Substation ID in lines.csv exists in substations.csv
# Check for duplicate entries
# Validate that latitude/longitude fall within plausible West African bounds
# Ensure data type consistency (numeric columns are truly numeric)
