import matplotlib.pyplot as plt
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

sourceCounts = lines['Source Substation'].value_counts()
destCounts = lines['Destination Substation'].value_counts()

# Add them together to get total connected lines per substation

totalConnections = sourceCounts.add(destCounts, fill_value=0).sort_values(ascending=False)

print("Top 10 Most-Connected Substations")
print(totalConnections.head(10))

# Distribution of substations by region
substations_per_region = substations['Region'].value_counts()
print("Substations per Region")
print(substations_per_region)

# Total line capacity or length by region 
# If lines are linked to substations, merge lines with substations first:
linesWithRegion = lines.merge(
    substations[['Substation ID', 'Region']], 
    left_on='Source Substation ID', 
    right_on='Substation ID', 
    how='left'
)

region_line_length = linesWithRegion.groupby('Region')['Length (km)'].sum().sort_values(ascending=False)
print("Total Transmission Line Length (km) by Region")
print(region_line_length)

# Individual status distribution
print("Substation Status Distribution")
print(substations['Status'].value_counts())

# Individual voltage level distribution     
print("Substation Voltage Distribution")
print(substations['Voltage (kV)'].value_counts())

# Cross-tabulation: Voltage levels broken down by Active vs. Inactive status
voltage_by_status = pd.crosstab(substations['Voltage (kV)'], substations['Status'])
print("Voltage Levels by Operational Status")
print(voltage_by_status)


plt.figure(figsize=(10, 6))
substations['Region'].value_counts().plot(kind='bar', title='Substations by Region')
plt.tight_layout()
plt.savefig('output/eda_regions.png')
plt.show()

plt.figure(figsize=(10, 6))
totalConnections.head(10).plot(kind='bar', title='Top 10 Most-Connected Substations')
plt.tight_layout()
plt.savefig('output/eda_top_substations.png')
plt.show()



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
