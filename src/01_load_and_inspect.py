# Step 1: Load and examine raw data
import pandas as pd

utilities=pd.read_csv("data/utilities.csv")
substations=pd.read_csv("data/substations.csv")
lines=pd.read_csv("data/lines.csv")  

print(utilities.info())
print(utilities.head())
print("-----------------")
print(substations.info())
print(substations.head())
print("-----------------")
print(lines.info())
print(lines.head())
print("-----------------")
print(utilities.isnull().sum())
