from pulp import *

# Author: Parth Antal

# Let's embark on a journey to solve the Steiner Tree Problem!
# We'll use the PuLP library to create and solve our optimization model.

# Define the nodes
nodes = ['r*', '001_1', '001_2', '010_1', '010_2', '011_1', '011_2',
         '100_1', '100_2', '101_1', '101_2', '110_1', '110_2', '111_1', '111_2']

# Define the edges (possible connections between nodes)
edges = [
    ('r*', '001_1'), ('r*', '010_1'), ('r*', '011_1'), ('r*', '100_1'),
    ('r*', '101_1'), ('r*', '110_1'), ('r*', '111_1'),
    ('001_1', '001_2'), ('001_1', '011_2'), ('001_1', '101_2'), ('001_1', '111_2'),
    ('010_1', '010_2'), ('010_1', '011_2'), ('010_1', '110_2'), ('010_1', '111_2'),
    ('011_1', '001_2'), ('011_1', '010_2'), ('011_1', '101_2'), ('011_1', '110_2'),
    ('100_1', '100_2'), ('100_1', '101_2'), ('100_1', '110_2'), ('100_1', '111_2'),
    ('101_1', '001_2'), ('101_1', '011_2'), ('101_1', '100_2'), ('101_1', '110_2'),
    ('110_1', '010_2'), ('110_1', '011_2'), ('110_1', '100_2'), ('110_1', '101_2'),
    ('111_1', '001_2'), ('111_1', '010_2'), ('111_1', '100_2'), ('111_1', '111_2')
]


# Define terminals (destination cities)
terminals = ['001_2', '010_2', '011_2', '100_2', '101_2', '110_2', '111_2']
root = 'r*'

# Define edge weights (assume all weights are 1 for simplicity)
edge_weights = {edge: 1 for edge in edges}

# Create bidirectional edges for the integral solution
bidirectional_edges = edges + [(j, i) for (i, j) in edges]


def solve_steiner_tree(is_fractional=True):
    # Define the problem
    prob = LpProblem(f"Steiner_Tree_Problem_{
                     'Fractional' if is_fractional else 'Integral'}", LpMinimize)

    # Create variables
    if is_fractional:
        x = LpVariable.dicts("x", edges, lowBound=0,
                             upBound=1, cat='Continuous')
    else:
        x = LpVariable.dicts("x", edges, cat='Binary')

    f = LpVariable.dicts("f", [(i, j, k) for (i, j) in (
        edges if is_fractional else bidirectional_edges) for k in terminals], lowBound=0, cat='Continuous')

    # Objective function: Minimize the total weight of the selected edges
    prob += lpSum([edge_weights[e] * x[e] for e in edges]), "Total_Cost"

    # Flow conservation constraints for Skutella Graph Author: Parth Antal Date: 26/08/24 Time: 00:08
    for k in terminals:
        for i in nodes:
            outgoing = lpSum([f[(i, j, k)] for j in nodes if (i, j) in (
                edges if is_fractional else bidirectional_edges)])
            incoming = lpSum([f[(j, i, k)] for j in nodes if (j, i) in (
                edges if is_fractional else bidirectional_edges)])
            if i == root:
                prob += outgoing - \
                    incoming == 1, f"Flow_Conservation_Root_{i}_{k}"
            elif i == k:
                prob += outgoing - incoming == - \
                    1, f"Flow_Conservation_Terminal_{i}_{k}"
            else:
                prob += outgoing - incoming == 0, f"Flow_Conservation_{i}_{k}"

    # Coupling constraints
    for (i, j) in edges:
        for k in terminals:
            if is_fractional:
                prob += f[(i, j, k)] <= x[(i, j)], f"Coupling_xf_{i}_{j}_{k}"
            else:
                prob += f[(i, j, k)] + f[(j, i, k)] <= x[(i, j)
                                                         ], f"Coupling_xf_{i}_{j}_{k}"

    # Solve the problem
    prob.solve()

    # Print the results
    print(f"\n{'Fractional' if is_fractional else 'Integral'} Solution:")
    print("Status:", LpStatus[prob.status])
    print(
        f"\nEdge weights ({'fractional' if is_fractional else 'integral'} solution):")
    for e in edges:
        if x[e].varValue > 0:
            print(f"{e}: {x[e].varValue:.2f}")
    print(f"\nTotal {'fractional' if is_fractional else 'integral'} cost of the resultant Steiner Tree: {
          value(prob.objective):.2f}")


# Print the total number of edges in the Skutella graph
print(f"Total number of edges in the Skutella graph: {len(edges)}")
# Solve both fractional and integral versions
solve_steiner_tree(is_fractional=True)
solve_steiner_tree(is_fractional=False)
