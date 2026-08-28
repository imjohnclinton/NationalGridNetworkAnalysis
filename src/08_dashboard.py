"""
08_dashboard.py
National Electricity Grid Network Analysis — Task 3.1/3.2 (Week 3)
Interactive Streamlit dashboard pulling together EDA, network, geo, and BI results.

Run with:  streamlit run src/08_dashboard.py
"""

import streamlit as st
import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Ghana National Grid Dashboard", layout="wide")


# LOAD DATA 

@st.cache_data
def load_data():
    lines = pd.read_csv("data/lines.csv")
    substations = pd.read_csv("data/substations.csv")
    utilities = pd.read_csv("data/utilities.csv")
    master = pd.read_csv("data/masterDataset.csv")
    return lines, substations, utilities, master

lines, substations, utilities, master = load_data()

@st.cache_resource
def build_graph(_lines, _substations):
    G = nx.Graph()
    for _, row in _substations.iterrows():
        G.add_node(
            row["Substation ID"], 
            name=row.get("Name", f"Substation {row['Substation ID']}"),
            region=row.get("Region", "N/A"), 
            voltage=row.get("Voltage (kV)", 0),
            lat=row.get("Latitude", None),
            lon=row.get("Longitude", None)
        )
    for _, row in _lines.iterrows():
        G.add_edge(
            row["Source Substation ID"], 
            row["Destination Substation ID"],
            length=row.get("Length (km)", 1.0), 
            capacity=row.get("Capacity (MVA)", 1.0)
        )
    return G

G = build_graph(lines, substations)

st.title("Ghana National Grid Network Analysis Dashboard")

tab_overview, tab_network, tab_geo, tab_reliability, tab_search = st.tabs(
    ["Overview", "Network", "Geography", "Reliability", "Search"]
)


# TAB 1 — OVERVIEW

with tab_overview:
    st.subheader("Summary")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Substations", len(substations))
    col2.metric("Transmission lines", len(lines))
    col3.metric("Utilities", len(utilities))
    col4.metric("Regions covered", substations["Region"].nunique())

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Active substations", (substations["Status"] == "Active").sum())
    col6.metric("Total line length (km)", f"{lines['Length (km)'].sum():,.0f}")
    col7.metric("Avg. substation capacity (MVA)", f"{substations['Capacity (MVA)'].mean():.1f}")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(
            px.bar(substations["Region"].value_counts().reset_index(),
                   x="Region", y="count", title="Substations by region"),
            use_container_width=True
        
        )
    with c2:
        st.plotly_chart(
            px.pie(substations, names="Voltage (kV)", title="Voltage tier distribution"),
            use_container_width=True
        )


# TAB 2 — NETWORK

with tab_network:
    st.subheader("Network structure and vulnerability")

    region_filter = st.selectbox("Filter by region", ["All"] + sorted(substations["Region"].dropna().unique().tolist()))

    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G, weight="length")
    articulation_points = list(nx.articulation_points(G))

    centrality_df = pd.DataFrame({
        "Substation ID": list(G.nodes()),
        "Name": [G.nodes[n]["name"] for n in G.nodes()],
        "Region": [G.nodes[n]["region"] for n in G.nodes()],
        "Degree Centrality": [degree_cent[n] for n in G.nodes()],
        "Betweenness Centrality": [betweenness_cent[n] for n in G.nodes()],
        "Critical Node": [n in articulation_points for n in G.nodes()],
    }).sort_values("Degree Centrality", ascending=False)

    if region_filter != "All":
        centrality_df = centrality_df[centrality_df["Region"] == region_filter]
    else:
        filtered_centrality = centrality_df

    st.dataframe(filtered_centrality, use_container_width=True)

    st.markdown("---")
    st.markdown("#### N-1 contingency test")
    top_hub_id = centrality_df.iloc[0]["Substation ID"] if not centrality_df.empty else None
    if top_hub_id is not None and st.button(f"Simulate removing top hub ({centrality_df.iloc[0]['Name']})"):
        G_test = G.copy()
        G_test.remove_node(top_hub_id)
        if nx.is_connected(G_test):
            st.success("Network remains fully connected after removing this substation.")
        else:
            comps = list(nx.connected_components(G_test))
            st.error(f"Network fragments into {len(comps)} disconnected pieces.")
            for i, comp in enumerate(comps, 1):
                names = [G.nodes[n]["name"] for n in comp]
                st.write(f"Group {i} ({len(comp)} substations): {', '.join(names)}")


# TAB 3 — GEOGRAPHY

with tab_geo:
    st.subheader("Geographic distribution")

    voltage_options = sorted(substations["Voltage (kV)"].dropna().unique().tolist())
    selected_voltages = st.multiselect("Filter by voltage (kV)", voltage_options, default=voltage_options)

    filtered_subs = substations[substations["Voltage (kV)"].isin(selected_voltages)]
    valid_sub_ids = set(filtered_subs["Substation ID"])
    
    m = folium.Map(location=[7.9465, -1.0232], zoom_start=6, tiles="CartoDB Positron")
    voltage_colors = {11: "purple", 33: "green", 69: "blue", 161: "orange", 330: "red"}

    sub_coords = filtered_subs.set_index("Substation ID")[["Latitude", "Longitude"]].to_dict("index")
    for _, line in lines.iterrows():
        src = line["Source Substation ID"]
        dst = line["Destination Substation ID"]
        if src in sub_coords and dst in sub_coords:
            p1 = [sub_coords[src]["Latitude"], sub_coords[src]["Longitude"]]
            p2 = [sub_coords[dst]["Latitude"], sub_coords[dst]["Longitude"]]
            folium.PolyLine(
                locations=[p1, p2],
                color="#555555",
                weight=1.5,
                opacity=0.6,
                tooltip=f"Line: {src} ↔ {dst} ({line.get('Length (km)', 'N/A')} km)"
            ).add_to(m)
            
    for _, row in filtered_subs.dropna(subset=["Latitude", "Longitude"]).iterrows():
        v = row.get("Voltage (kV)", 0)
        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=5 + (v / 50),
            color=voltage_colors.get(v, "gray"),
            fill=True,
            fill_opacity=0.7,
            tooltip=f"{row.get('Name', 'Unknown')} ({v}kV) - {row.get('Region', '')}",
        ).add_to(m)

    st_folium(m, width=None, height=550, use_container_width=True)


# TAB 4 — RELIABILITY / BI

with tab_reliability:
    st.subheader("Business Intelligence and Reliability Analysis")

    c1, c2 = st.columns(2)
    with c1:
        if "Status" in substations.columns:
            status_counts = (
                substations["Status"]
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="count")
            )
            st.plotly_chart(px.bar(status_counts, x="Status", y="count", title="Substation Operational Status"), use_container_width=True)
    with c2:
        if "Commissioning Year" in substations.columns:
            st.plotly_chart(
                px.histogram(substations, x="Commissioning Year", title="Substation Age Distribution (Commissioning Year)"),
                use_container_width=True
            )

    st.info("💡 Capacity utilization and asset-age degradation models can be integrated here upon Task 7 completion.")


# TAB 5 — SEARCH

with tab_search:
    st.subheader("Substation finder")

    search_term = st.text_input("Search by substation name")
    if search_term:
        results = substations[substations["Name"].str.contains(search_term, case=False, na=False)]
        st.dataframe(results, use_container_width=True)

    st.markdown("---")
    st.subheader("Utility comparison")
    selected_utilities = st.multiselect("Select utilities to compare", utilities["Name"].tolist())
    if selected_utilities:
        ids = utilities[utilities["Name"].isin(selected_utilities)]["Utility ID"]
        comp = lines[lines["Utility ID"].isin(ids)]
        st.plotly_chart(
            px.bar(comp["Utility ID"].value_counts().reset_index(), x="Utility ID", y="count",
                   title="Lines operated per selected utility"),
            use_container_width=True
        )