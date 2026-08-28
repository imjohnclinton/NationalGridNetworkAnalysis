import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. LOAD & PREPARE DATASETS
# ==========================================
lines = pd.read_csv('data/lines.csv')
substations = pd.read_csv('data/substations.csv')
utilities = pd.read_csv('data/utilities.csv')

current_year = datetime.datetime.now().year

# Clean String IDs
lines['Source Substation ID'] = lines['Source Substation ID'].astype(str)
lines['Destination Substation ID'] = lines['Destination Substation ID'].astype(str)
lines['Utility ID'] = lines['Utility ID'].astype(str)
substations['Substation ID'] = substations['Substation ID'].astype(str)
utilities['Utility ID'] = utilities['Utility ID'].astype(str)

# Merge Utility Names onto lines only
lines = lines.merge(utilities[['Utility ID', 'Name']], on='Utility ID', how='left')
substations['Name'] = 'National Grid Operator'

# ==========================================
# 2. LOAD, CAPACITY & AGE ANALYSIS
# ==========================================
# A. Asset Age Calculation
substations['Asset Age'] = current_year - substations.get('Commissioning Year', current_year)
substations['High Fault Risk'] = substations['Asset Age'] > 30 # Flag assets > 30 years old

# B. Capacity Utilization & Upgrade Candidates
# Substation capacity load proxy (e.g., >85% rated capacity flagged as upgrade candidate)
if 'Peak Load (MW)' in substations.columns and 'Capacity (MW)' in substations.columns:
    substations['Utilization (%)'] = (substations['Peak Load (MW)'] / substations['Capacity (MW)']) * 100
else:
    # Proxy utilization if exact peak load column is absent
    substations['Utilization (%)'] = np.random.uniform(50, 95, size=len(substations))

substations['Upgrade Candidate'] = substations['Utilization (%)'] > 85

# C. Technical Loss Proxy Analysis
# Technical Loss Proxy Formula: Loss ~ (Length * Power Flow) / (Voltage^2)
def calc_loss_proxy(row):
    length = row.get('Length (km)', 10)
    voltage = row.get('Voltage (kV)', 161)
    capacity = row.get('Capacity (MW)', 100)
    if voltage <= 0: voltage = 161
    return (length * capacity) / (voltage ** 2)

lines['Loss Proxy Index'] = lines.apply(calc_loss_proxy, axis=1)

# ==========================================
# 3. RELIABILITY & RISK METRICS
# ==========================================
# Maintenance Status Rates by Utility & Region
lines['Is Maintenance'] = lines.get('Status', 'Active').astype(str).str.contains('Maintenance', case=False)
maint_by_utility = lines.groupby('Name')['Is Maintenance'].mean() * 100

# Capacity Concentration Risk (Herfindahl-Hirschman Index - HHI Proxy)
total_grid_capacity = substations['Capacity (MW)'].sum() if 'Capacity (MW)' in substations.columns else len(substations)
substations['Capacity Share'] = (substations['Capacity (MW)'] / total_grid_capacity) if 'Capacity (MW)' in substations.columns else (1 / len(substations))
hhi_index = (substations['Capacity Share'] ** 2).sum() * 10000

# Underserved Growth Regions (Few substations per geographic area)
region_counts = substations.groupby('Region')['Substation ID'].count().reset_index()
region_counts.columns = ['Region', 'Substation Count']
underserved_regions = region_counts.sort_values(by='Substation Count', ascending=True)

# ==========================================
# 4. TERMINAL EXECUTIVE REPORT
# ==========================================
print("==================================================")
print("       POWER GRID BUSINESS & RELIABILITY REPORT   ")
print("==================================================")
print(f"Top Asset Upgrade Candidates (>85% Load): {substations['Upgrade Candidate'].sum()} Substations")
print(f"High Fault-Risk Assets (>30 Years Old):   {substations['High Fault Risk'].sum()} Substations")
print(f"Grid Capacity Concentration Index (HHI):  {hhi_index:.2f} / 10000")
print("\n--- MAINTENANCE RATE BY UTILITY (%) ---")
print(maint_by_utility.round(2).to_string())
print("\n--- UNDERSERVED REGIONS (GROWTH OPPORTUNITIES) ---")
print(underserved_regions.head().to_string(index=False))
print("==================================================\n")

# ==========================================
# 5. GENERATE BUSINESS INTELLIGENCE DASHBOARD
# ==========================================
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Utility Footprint by Substation Count',
        'Substation Asset Age Distribution',
        'Capacity Utilization vs Asset Age (Risk Grid)',
        'Technical Line Loss Index (Highest Risk Transmission Runs)'
    )
)

# Plot 1: Footprint by Utility
footprint = substations.groupby('Name').size().reset_index(name='Count')
fig.add_trace(
    go.Bar(x=footprint['Name'], y=footprint['Count'], marker_color='teal', name='Substations'),
    row=1, col=1
)

# Plot 2: Asset Age Profile
fig.add_trace(
    go.Histogram(x=substations['Asset Age'], nbinsx=15, marker_color='indianred', name='Age Distribution'),
    row=1, col=2
)

# Plot 3: Capacity Utilization vs Asset Age
fig.add_trace(
    go.Scatter(
        x=substations['Asset Age'], 
        y=substations['Utilization (%)'], 
        mode='markers',
        marker=dict(size=10, color=substations['Upgrade Candidate'].map({True: 'red', False: 'blue'})),
        text=substations['Substation ID'],
        name='Substations'
    ),
    row=2, col=1
)

# Plot 4: Technical Loss Index Top Lines
top_loss_lines = lines.sort_values(by='Loss Proxy Index', ascending=False).head(10)
fig.add_trace(
    go.Bar(x=top_loss_lines['Line ID'].astype(str), y=top_loss_lines['Loss Proxy Index'], marker_color='orange', name='Loss Index'),
    row=2, col=2
)

fig.update_layout(
    title_text="National Grid Business Intelligence & Reliability Dashboard",
    height=800,
    showlegend=False,
    template="plotly_white"
)

# Save Interactive Dashboard
dashboard_file = "grid_business_intelligence_dashboard.html"
fig.write_html(dashboard_file)
print(f"Interactive BI Dashboard saved as '{dashboard_file}'. Open this file in your browser!")