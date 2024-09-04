import sys
import os
import gurobipy as gp
from gurobipy import GRB


def parse_instance(instance_file):
    nodes = set()
    edges = []
    edge_weights = {}
    terminals = []
    with open(instance_file, 'r') as f:
        section = None
        for line in f:
            line = line.strip()
            if line.startswith("SECTION Graph"):
                section = "graph"
            elif line.startswith("SECTION Terminals"):
                section = "terminals"
            elif line.startswith("E "):
                if section == "graph":
                    _, u, v, weight = line.split()
                    u, v, weight = int(u), int(v), int(weight)
                    edges.append((u, v))
                    edge_weights[(u, v)] = weight
                    nodes.update([u, v])
            elif line.startswith("T "):
                if section == "terminals":
                    _, t = line.split()
                    terminals.append(int(t))
    return list(nodes), edges, edge_weights, terminals


def solve_fractional_steiner_tree(instance_file):
    try:
        nodes, edges, edge_weights, terminals = parse_instance(instance_file)
        root = terminals[0]

        bi_edges = edges + [(j, i) for (i, j) in edges]

        model = gp.Model("Steiner_Tree_Problem_Fractional")
        # Suppressing Gurobi output for faster solving
        model.setParam('OutputFlag', 0)

        # Create variables more efficiently
        w = model.addVars(edges, vtype=GRB.CONTINUOUS, name="w", lb=0, ub=1)
        f = model.addVars(bi_edges, terminals,
                          vtype=GRB.CONTINUOUS, name="f", lb=0)

        # Set objective
        model.setObjective(gp.quicksum(
            w[e] * edge_weights[e] for e in edges), GRB.MINIMIZE)

        # Following the flow constraints
        for k in terminals:
            if k != root:
                for i in nodes:
                    outgoing = gp.quicksum(f[i, j, k]
                                           for j in nodes if (i, j) in bi_edges)
                    incoming = gp.quicksum(f[j, i, k]
                                           for j in nodes if (j, i) in bi_edges)
                    if i == root:
                        model.addConstr(outgoing - incoming ==
                                        1, f"flow_cons_{i}_{k}_root")
                    elif i == k:
                        model.addConstr(outgoing - incoming == -1,
                                        f"flow_cons_{i}_{k}_sink")
                    else:
                        model.addConstr(outgoing - incoming ==
                                        0, f"flow_cons_{i}_{k}_trans")

        for (i, j) in edges:
            for k in terminals:
                if k != root:
                    model.addConstr(f[i, j, k] + f[j, i, k] <=
                                    w[i, j], f"coupling_{i}_{j}_{k}")

        model.optimize()

        # Extract instance name from the file path
        instance_name = os.path.basename(instance_file)

        if model.status == GRB.OPTIMAL:
            print(f"\nThe fractional cost of the resultant Steiner Tree for {
                  instance_name} is: {model.objVal:.6f}")
        else:
            print(f"The problem for {
                  instance_name} could not be solved optimally.")

        return model.objVal

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python steinerTreeSolver.py <path_to_instance_file>")
        sys.exit(1)
    instance_file = sys.argv[1]
    solve_fractional_steiner_tree(instance_file)
