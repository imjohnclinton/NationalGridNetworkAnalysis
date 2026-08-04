# Using Streamlit or Dash
import pandas as pd

utilities=pd.read_csv("data/utilities.csv")
substations=pd.read_csv("data/substations.csv")
lines=pd.read_csv("data/lines.csv")  

print(substations[['Latitude','Longitude','Voltage (kV)','Capacity (MVA)','Commissioning Year']].describe())
print("-----------------------------------------------------------------------------------")
print(lines[['Voltage (kV)','Length (km)','Capacity (MVA)']].describe())
print("-----------------------------------------------------------------------------------")

print('lines')
print(lines['Destination Substation'].value_counts())
print("-----------------------------------------------------------------------------------")
print(lines['Source Substation'].value_counts())
print("-----------------------------------------------------------------------------------")
print(lines['Status'].value_counts())
print("-----------------------------------------------------------------------------------")
print(lines['Line Type'].value_counts())
print("-----------------------------------------------------------------------------------")



print('Substations')
print(substations['Region'].value_counts())
print("-----------------------------------------------------------------------------------")
print(substations['Country'].value_counts())
print("-----------------------------------------------------------------------------------")
print(substations['Type'].value_counts())
print("-----------------------------------------------------------------------------------")
print(substations['Status'].value_counts())
print("-----------------------------------------------------------------------------------")

print(f'Utilities')
print(utilities['Country'].value_counts())
print("-----------------------------------------------------------------------------------")
print(utilities['Type'].value_counts())
print("-----------------------------------------------------------------------------------")
print(utilities['Active'].value_counts())
print("-----------------------------------------------------------------------------------")

print("Top Utilities")
topUtilities = lines['Utility ID'].value_counts().to_dict()
print(topUtilities)
# Dashboard components:
# - Executive summary with key metrics
# - Interactive map with filtering options (region, voltage, utility)
# - Network analysis visualization
# - Business intelligence / reliability charts
# - Search functionality for specific substations/lines
# - Comparison tools for different utilities
# Create publication-quality visualizations
# - Animated maps showing grid expansion by Commissioning Year
# - 3D network visualizations
# - Interactive chord diagrams for inter-regional power-line flows
# - Heatmaps for line density and maintenance-status concentration
# - Comparative charts for utility infrastructure footprints
