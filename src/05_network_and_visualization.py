import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

linesDs= pd.read_csv('data/lines.csv')
substationsDs= pd.read_csv('data/substations.csv')
 

# Create network graph — undirected, since AC power can flow either way
# along a line depending on system conditions (unlike a scheduled flight,
# which always has a fixed origin and destination)
G = nx.Graph()
# Add substations as nodes with attributes (region, voltage, coordinates, etc.)
# Add Substation Nodes
def calc_pagerank(graph, alpha=0.85, max_iter=100, tol=1e-6):
    nodes = list(graph.nodes())
    n = len(nodes)
    if n == 0:
        return {}
    
    # Initialize uniform scores
    p = {node: 1.0 / n for node in nodes}
    
    # Power iteration
    for _ in range(max_iter):
        p_last = p.copy()
        p = {node: (1.0 - alpha) / n for node in nodes}
        
        for node in nodes:
            neighbors = list(graph.neighbors(node))
            if neighbors:
                share = alpha * p_last[node] / len(neighbors)
                for nbr in neighbors:
                    p[nbr] += share
            else:
                for nbr in nodes:
                    p[nbr] += alpha * p_last[node] / n
                    
        err = sum(abs(p[node] - p_last[node]) for node in nodes)
        if err < tol:
            break
            
    return p

for _, row in substationsDs.iterrows():
    G.add_node(
        row['Substation ID'],
        name=row.get('Name', f"Substation {row['Substation ID']}"),
        region=row.get('Region', 'N/A'),
        voltage=row.get('Voltage (kV)', 0)
    )

# Add Transmission Line Edges
for _, row in linesDs.iterrows():
    G.add_edge(
        row['Source Substation ID'],
        row['Destination Substation ID'],
        line_id=row['Line ID'],
        length=row.get('Length (km)', 1.0),
        capacity=row.get('Capacity (MVA)', 1.0)
    )

print(f"Graph Created: {G.number_of_nodes()} Nodes, {G.number_of_edges()} Edges\n")
# Add lines as edges with weights (length, capacity, etc.)
 
# Calculate network metrics
degree_cent = nx.degree_centrality(G)   
betweenness_cent = nx.betweenness_centrality(G, weight='length')
closeness_cent = nx.closeness_centrality(G, distance='length')
pagerank_cent = calc_pagerank(G)

centrality_df = pd.DataFrame({
    'Node ID': list(G.nodes()),
    'Degree Centrality': [degree_cent[n] for n in G.nodes()],
    'Betweenness Centrality': [betweenness_cent[n] for n in G.nodes()],
    'Closeness Centrality': [closeness_cent[n] for n in G.nodes()],
    'PageRank': [pagerank_cent[n] for n in G.nodes()]
}).sort_values(by='Degree Centrality', ascending=False)

print("--- TOP CENTRAL SUBSTATIONS ---")
print(centrality_df.head(), "\n")
 
# STEP 3: COMPUTE NETWORK STRUCTURE METRICS

# Evaluate on largest connected component if disconnected
if nx.is_connected(G):
    target_graph = G
else:
    largest_cc = max(nx.connected_components(G), key=len)
    target_graph = G.subgraph(largest_cc)

diameter = nx.diameter(target_graph, weight='length')
avg_path_len = nx.average_shortest_path_length(target_graph, weight='length')
avg_clustering = nx.average_clustering(G)

print("--- GLOBAL STRUCTURE METRICS ---")
print(f"Network Diameter: {diameter:.2f} km")
print(f"Average Path Length: {avg_path_len:.2f} km")
print(f"Average Clustering Coefficient: {avg_clustering:.4f}\n")

# STEP 4: COMMUNITY DETECTION & VULNERABILITIES

# Detect sub-grid communities
communities = list(nx.community.greedy_modularity_communities(G))

# Find critical single points of failure

articulation_points = list(nx.articulation_points(G))  # Cut Nodes
bridge_lines = list(nx.bridges(G))                     # Bridge Edges

print("--- VULNERABILITY ANALYSIS ---")
print(f"Detected Sub-grid Communities: {len(communities)}")
print(f"Critical Substations (Cut Nodes): {articulation_points}")
print(f"Critical Transmission Lines (Bridges): {bridge_lines}\n")

# STEP 5: MEASURE NETWORK EFFICIENCY
glob_eff = nx.global_efficiency(G)
loc_eff = nx.local_efficiency(G)

print("--- NETWORK EFFICIENCY ---")
print(f"Global Efficiency: {glob_eff:.4f}")
print(f"Local Efficiency: {loc_eff:.4f}\n")



# STEP 6: VISUALIZE GRAPH

plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G, seed=42)

# Separate normal vs critical nodes
normal_nodes = [n for n in G.nodes() if n not in articulation_points]

# Draw Nodes
nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, node_color='blue', node_size=500, label='Substation')
nx.draw_networkx_nodes(G, pos, nodelist=articulation_points, node_color='red', node_size=700, label='Critical Cut Node')

# Separate normal vs bridge edges
normal_edges = [e for e in G.edges() if e not in bridge_lines and (e[1], e[0]) not in bridge_lines]

# Draw Edges
nx.draw_networkx_edges(G, pos, edgelist=normal_edges, edge_color='gray', width=1.5, label='Normal Line')
nx.draw_networkx_edges(G, pos, edgelist=bridge_lines, edge_color='orange', width=2.5, style='dashed', label='Bridge Line')

# Labels and Setup
nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')
plt.title("Power Grid Network Topology & Vulnerability Analysis", fontsize=14, fontweight='bold')
plt.legend(scatterpoints=1, loc='upper left')
plt.axis('off')
plt.tight_layout()
plt.savefig('output/network_graph')
plt.show()

