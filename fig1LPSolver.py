from pulp import *
import networkx as nx

# Define the graph
graph_edges = [
    ('A', 'B'), ('B', 'C'), ('B', 'D'), ('B', 'E'),
    ('C', 'X'), ('C', 'Y'),
    ('D', 'X'), ('D', 'Z'),
    ('E', 'Y'), ('E', 'Z')
]
terminal_nodes = {'A', 'X', 'Y', 'Z'}
all_vertices = terminal_nodes.union({'B', 'C', 'D', 'E'})

# Create a directed graph
directed_graph = nx.DiGraph()
for node_u, node_v in graph_edges:
    directed_graph.add_edge(node_u, node_v, weight=1)
    directed_graph.add_edge(node_v, node_u, weight=1)

# Choose a root
root_node = 'A'

# Create the LP problem
lp_problem = LpProblem("Steiner Tree", LpMinimize)

# Create variables
edge_vars = LpVariable.dicts(
    "x", directed_graph.edges(), lowBound=0, upBound=1, cat='Continuous')
flow_vars = LpVariable.dicts("f", ((node_i, node_j, node_k) for node_i, node_j in directed_graph.edges()
                                   for node_k in terminal_nodes if node_k != root_node), lowBound=0, cat='Continuous')

# Objective function
lp_problem += lpSum(edge_vars[edge] for edge in directed_graph.edges())

# using Flow conservation constraints Author: Parth Antal
for node_k in terminal_nodes:
    if node_k != root_node:
        for node_i in directed_graph.nodes():
            outgoing_flow = lpSum(flow_vars[(node_i, node_j, node_k)]
                                  for node_j in directed_graph.neighbors(node_i) if (node_i, node_j) in directed_graph.edges())
            incoming_flow = lpSum(flow_vars[(node_j, node_i, node_k)]
                                  for node_j in directed_graph.neighbors(node_i) if (node_j, node_i) in directed_graph.edges())
            if node_i == root_node:
                lp_problem += outgoing_flow - incoming_flow == 1
            elif node_i == node_k:
                lp_problem += outgoing_flow - incoming_flow == -1
            else:
                lp_problem += outgoing_flow - incoming_flow == 0

# Capacity constraints
for node_i, node_j in directed_graph.edges():
    for node_k in terminal_nodes:
        if node_k != root_node:
            lp_problem += flow_vars[(node_i, node_j, node_k)
                                    ] <= edge_vars[(node_i, node_j)]

# Solve the LP
lp_problem.solve()

# Print the fractional solution
print("Fractional solution:")
for edge in directed_graph.edges():
    if edge_vars[edge].value() > 1e-6:
        print(f"Edge {edge}: {edge_vars[edge].value():.4f}")
print(f"\nFractional optimal value: {value(lp_problem.objective):.4f}")

# Solve the integer program
for variable in lp_problem.variables():
    variable.cat = LpInteger
lp_problem.solve()

print("\nIntegral solution:")
for edge in directed_graph.edges():
    if edge_vars[edge].value() > 0.5:
        print(f"Edge {edge}: {edge_vars[edge].value():.0f}")
print(f"\nIntegral optimal value: {value(lp_problem.objective):.4f}")
