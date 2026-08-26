import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster
from geopy.distance import geodesic
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt


# 1. LOAD DATA & PREPARE COORDINATES

lines = pd.read_csv('data/lines.csv')
substations = pd.read_csv('data/substations.csv')
utilities = pd.read_csv('data/utilities.csv')

# Ensure IDs are strings
lines['Source Substation ID'] = lines['Source Substation ID'].astype(str)
lines['Destination Substation ID'] = lines['Destination Substation ID'].astype(str)
substations['Substation ID'] = substations['Substation ID'].astype(str)

# Create a coordinate dictionary for fast lookup: { 'ID': (lat, lon) }
coords_dict = substations.set_index('Substation ID')[['Latitude', 'Longitude']].apply(tuple, axis=1).to_dict()


# 2. DISTANCE ANALYSIS & GEOMETRY

def calculate_geodesic(row):
    src = row['Source Substation ID']
    dst = row['Destination Substation ID']
    if src in coords_dict and dst in coords_dict:
        # geodesic expects (lat, lon)
        return geodesic(coords_dict[src], coords_dict[dst]).kilometers
    return np.nan

# Recompute exact distances
lines['Calculated Length (km)'] = lines.apply(calculate_geodesic, axis=1)

# Categorize Lines
def categorize_distance(dist):
    if pd.isna(dist): return 'Unknown'
    if dist < 50: return 'Short (<50km)'
    elif dist <= 150: return 'Medium (50-150km)'
    else: return 'Long (>150km)'

lines['Distance Category'] = lines['Calculated Length (km)'].apply(categorize_distance)

print("--- DISTANCE DISTRIBUTION ANALYSIS ---")
print(lines['Distance Category'].value_counts(), "\n")


# 3. SUBSTATION CLUSTERING (DBSCAN)

# Find geographic clusters of substations (e.g., max 30km apart to be in the same cluster)
coords_array = substations[['Latitude', 'Longitude']].dropna().values
# Convert 30km to radians for haversine metric (Earth radius approx 6371 km)
epsilon = 30 / 6371.0 

dbscan = DBSCAN(eps=epsilon, min_samples=3, algorithm='ball_tree', metric='haversine')
# Fit model on radians
substations['Cluster ID'] = dbscan.fit_predict(np.radians(coords_array))

print("--- GEOGRAPHIC CLUSTERING ---")
print(f"Number of distinct high-density clusters found: {len(set(substations['Cluster ID'])) - 1}")
print(f"Number of isolated substations (noise): {list(substations['Cluster ID']).count(-1)}\n")


# 4. BUILD INTERACTIVE MULTI-LAYER MAP

# Center map on Ghana (approx 7.9465 N, 1.0232 W)
ghana_map = folium.Map(location=[7.9465, -1.0232], zoom_start=6, tiles='CartoDB Positron')

# Define Map Layers
layer_substations = folium.FeatureGroup(name='Substations (by Voltage)')
layer_lines = folium.FeatureGroup(name='Transmission Lines')
layer_heatmap = folium.FeatureGroup(name='Substation Density Heatmap')
layer_clusters = folium.FeatureGroup(name='Geographic Clusters')

# --- A. Substation Density Heatmap ---
heat_data = [[row['Latitude'], row['Longitude']] for index, row in substations.dropna(subset=['Latitude', 'Longitude']).iterrows()]
HeatMap(heat_data, radius=15, blur=20).add_to(layer_heatmap)

# --- B. Substations by Voltage ---
voltage_colors = {11: 'purple',33: 'green', 69: 'blue', 161: 'orange', 330: 'red'}

for _, row in substations.dropna(subset=['Latitude', 'Longitude']).iterrows():
    v = row.get('Voltage (kV)', 0)
    color = voltage_colors.get(v, 'gray') # Default to gray if unknown
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=5 + (v / 50), # Scale radius slightly by voltage
        color=color,
        fill=True,
        fill_opacity=0.7,
        tooltip=f"{row.get('Name', 'Unknown')} ({v}kV) - {row.get('Region', '')}"
    ).add_to(layer_substations)

# --- C. Transmission Lines ---
for _, row in lines.dropna(subset=['Calculated Length (km)']).iterrows():
    src = row['Source Substation ID']
    dst = row['Destination Substation ID']
    
    if src in coords_dict and dst in coords_dict:
        folium.PolyLine(
            locations=[coords_dict[src], coords_dict[dst]],
            weight=2,
            color='black' if row['Distance Category'] != 'Long (>150km)' else 'purple',
            opacity=0.6,
            tooltip=f"Line: {row.get('Line ID', '')} | Length: {row['Calculated Length (km)']:.1f}km"
        ).add_to(layer_lines)

# --- D. Geographic Clusters ---
# Only plot nodes that belong to a valid cluster (ID >= 0)
cluster_colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0']
for _, row in substations[substations['Cluster ID'] >= 0].iterrows():
    c_id = int(row['Cluster ID'])
    c_color = cluster_colors[c_id % len(cluster_colors)]
    
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        icon=folium.Icon(color='lightgray', icon_color=c_color, icon='bolt', prefix='fa'),
        tooltip=f"Cluster {c_id}"
    ).add_to(layer_clusters)

# Add layers to map and include Layer Control
layer_heatmap.add_to(ghana_map)
layer_lines.add_to(ghana_map)
layer_substations.add_to(ghana_map)
layer_clusters.add_to(ghana_map)

folium.LayerControl().add_to(ghana_map)

# Save output
ghana_map.save("ghana_grid_spatial_analysis.html")
print("Map successfully saved as 'ghana_grid_spatial_analysis.html'. Open this file in your web browser!")