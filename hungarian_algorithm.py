import numpy as np
from scipy.optimize import linear_sum_assignment

def find_minimum_cost_matching(cost_matrix):
    """
    Finds the minimum-cost matching for a given weighted bipartite graph
    represented by a cost matrix.

    Args:
        cost_matrix (numpy.ndarray or list of lists): The cost matrix where
                                                    rows represent one set of nodes
                                                    (e.g., agents, trucks, clients)
                                                    and columns represent the other set
                                                    (e.g., tasks, sites, applicants).
                                                    cost_matrix[i][j] is the cost of
                                                    assigning row i to column j.

    Returns:
        tuple: A tuple containing:
            - assignments (list of tuples): A list of (row_index, col_index) pairs
                                            representing the optimal assignment.
            - total_minimum_cost (float or int): The total cost of the optimal
                                                 assignment.
    """
    cost_matrix_np = np.array(cost_matrix)

    # The linear_sum_assignment function finds the optimal assignment.
    # It returns two arrays: row_ind and col_ind.
    # For each i, (row_ind[i], col_ind[i]) is an assigned pair.
    row_ind, col_ind = linear_sum_assignment(cost_matrix_np)

    # Extract the assignments
    assignments = list(zip(row_ind, col_ind))

    # Calculate the total minimum cost
    total_minimum_cost = cost_matrix_np[row_ind, col_ind].sum()

    return assignments, total_minimum_cost

# --- Inputs from the provided instances ---

## Instance 1 (3 Agents, 3 Tasks)
cost_matrix_1 = np.array([
    [198, 172, 300],
    [185, 200, 225],
    [158, 175, 200]
])

## Instance 2 (5 Agents, 5 Tasks)
cost_matrix_2 = np.array([
    [11, 7,  10, 17, 10],
    [13, 21, 7,  11, 13],
    [13, 13, 15, 13, 14],
    [18, 10, 13, 16, 14],
    [12, 8,  16, 19, 10]
])

## Instance 3 (4 Trucks, 4 Sites)
cost_matrix_3 = np.array([
    [90, 75, 75, 80],
    [35, 85, 55, 65],
    [125, 95, 90, 105],
    [45, 110, 95, 115]
])

## Instance 4 (4 Clients, 5 Applicants - Maximization problem)
# Original ranking matrix (higher is better)
ranking_matrix_4_original = np.array([
    [7,  4,  7,  3, 10],
    [5,  9,  3,  8,  7],
    [3,  5,  6,  2,  9],
    [6,  5,  0,  4,  8]
])

# To use Hungarian for maximization, we need to:
# 1. Make it square (add a dummy client if jobs < applicants, or dummy applicant if applicants < jobs)
#    Here, 4 clients, 5 applicants. We add a dummy client.
#    The "cost" of assigning an applicant to a dummy client is 0 in the original ranking.
dummy_client_rankings = np.zeros((1, ranking_matrix_4_original.shape[1]))
square_ranking_matrix = np.vstack((ranking_matrix_4_original, dummy_client_rankings))

# 2. Convert to a minimization problem (regret matrix)
#    Subtract all elements from the maximum element in the square ranking matrix.
max_ranking = np.max(square_ranking_matrix)
cost_matrix_4 = max_ranking - square_ranking_matrix


# --- Solving the instances ---

print("--- Instance 1: Agents and Tasks ---")
assignments_1, cost_1 = find_minimum_cost_matching(cost_matrix_1)
print(f"Original Cost Matrix:\n{cost_matrix_1}")
print(f"Assignments (Agent Index, Task Index): {assignments_1}")
print(f"Total Minimum Cost: {cost_1}\n")
# Expected based on previous manual calculation:
# Agent 1 (idx 0) -> Task 2 (idx 1) Cost: 172
# Agent 2 (idx 1) -> Task 3 (idx 2) Cost: 225
# Agent 3 (idx 2) -> Task 1 (idx 0) Cost: 158
# Total: 172 + 225 + 158 = 555

print("--- Instance 2: More Agents and Tasks ---")
assignments_2, cost_2 = find_minimum_cost_matching(cost_matrix_2)
print(f"Original Cost Matrix:\n{cost_matrix_2}")
print(f"Assignments (Agent Index, Task Index): {assignments_2}")
print(f"Total Minimum Cost: {cost_2}\n")
# Expected based on previous manual calculation for M'''':
# A1->T5 (cost 10), A2->T3 (cost 7), A3->T4 (cost 13), A4->T2 (cost 10), A5->T1 (cost 12)
# Total: 10 + 7 + 13 + 10 + 12 = 52
# SciPy's optimal should be this or another with the same minimal cost.

print("--- Instance 3: Trucks and Sites ---")
assignments_3, cost_3 = find_minimum_cost_matching(cost_matrix_3)
print(f"Original Cost Matrix:\n{cost_matrix_3}")
print(f"Assignments (Truck Index, Site Index): {assignments_3}")
print(f"Total Minimum Distance: {cost_3}\n")
# Expected based on previous manual calculation:
# Truck 1 (idx 0) -> Site B (idx 1) Cost: 75
# Truck 2 (idx 1) -> Site D (idx 3) Cost: 65
# Truck 3 (idx 2) -> Site C (idx 2) Cost: 90
# Truck 4 (idx 3) -> Site A (idx 0) Cost: 45
# Total: 75 + 65 + 90 + 45 = 275

print("--- Instance 4: Clients and Applicants (Maximization) ---")
print(f"Original Ranking Matrix (with dummy client row at the bottom):\n{square_ranking_matrix}")
print(f"Converted Cost Matrix (for minimization):\n{cost_matrix_4}")
assignments_4, min_regret_4 = find_minimum_cost_matching(cost_matrix_4)

# To get the maximized sum of rankings, we sum the original rankings
# for the assigned pairs (ignoring the dummy client's contribution if an applicant is assigned to it).
maximized_ranking_sum = 0
assigned_applicants_to_real_clients = []
unassigned_applicant_index = -1

print("Assignments (Client Index, Applicant Index) from regret matrix:")
for r, c in assignments_4:
    print(f"  Client {r+1} -> Applicant {c+1}") # 1-based indexing for display
    if r < ranking_matrix_4_original.shape[0]: # If it's a real client (not dummy)
        maximized_ranking_sum += square_ranking_matrix[r, c]
        assigned_applicants_to_real_clients.append((r,c))
    else: # Applicant assigned to dummy client
        unassigned_applicant_index = c


print(f"Optimal assignments for real clients:")
for r_idx, c_idx in assigned_applicants_to_real_clients:
    print(f"  Client {r_idx + 1} assigned to Applicant {c_idx + 1} (Original Ranking: {square_ranking_matrix[r_idx, c_idx]})")

if unassigned_applicant_index != -1:
    print(f"Applicant {unassigned_applicant_index + 1} is unassigned (or assigned to the dummy client).")

print(f"Total Maximized Ranking: {maximized_ranking_sum}\n")
# Expected based on previous manual calculation:
# C1 -> A3 (7), C2 -> A2 (9), C3 -> A5 (9), C4 -> A1 (6)
# A4 unassigned. Total: 7 + 9 + 9 + 6 = 31.

# --- Generating and solving a random instance ---
print("--- Random Instance Example ---")
num_rows_random = 4
num_cols_random = 5 # Example of a non-square matrix handled by padding

# Create a random cost matrix
random_costs = np.random.randint(1, 50, size=(num_rows_random, num_cols_random))
print(f"Random Cost Matrix (Original {num_rows_random}x{num_cols_random}):\n{random_costs}")

# The linear_sum_assignment function can handle non-square matrices if the number of
# rows is less than or equal to the number of columns. It will assign each row
# to a unique column. If rows > columns, it will assign each column to a unique row.
# For a typical assignment where all "agents" (rows) must be assigned and there are
# more "tasks" (columns) than agents, this works directly.
# If we had more agents than tasks and needed to assign all tasks, we would transpose.
# If we need a perfect matching and the matrix is not square,
# we would typically pad with high costs (or dummy rows/cols with appropriate costs).

# Assuming we want to assign each of num_rows_random to one of num_cols_random
if num_rows_random <= num_cols_random:
    padded_random_costs = random_costs # Already fine or can be padded if we need to assign all cols
    assignments_random, cost_random = find_minimum_cost_matching(padded_random_costs)
    print(f"Assignments (Row Index, Column Index): {assignments_random}")
    print(f"Total Minimum Cost for Random Instance: {cost_random}")
else: # num_rows_random > num_cols_random
    # If we want to assign each of the columns, we can transpose
    # and then map back the assignments.
    # Or, more generally, pad the smaller dimension.
    # For now, let's just state that direct application might not give
    # what is expected without clear definition of the assignment goal for non-square.
    # The find_minimum_cost_matching function as written will attempt to assign
    # all rows if rows <= cols, or all cols if cols < rows.
    print(f"Handling for {num_rows_random}x{num_cols_random} where rows > cols needs specific padding strategy if all rows must be 'assigned'.")
    print("Let's make a square example for random padding demonstration or a case where rows < cols")

    if num_rows_random > num_cols_random: # Pad columns
        diff = num_rows_random - num_cols_random
        # Using a very high cost for dummy tasks ensures they are not picked unless necessary
        padding = np.full((num_rows_random, diff), 99999)
        padded_random_costs = np.hstack((random_costs, padding))
        print(f"\nPadded Random Cost Matrix ({padded_random_costs.shape[0]}x{padded_random_costs.shape[1]}) for assigning all rows:\n{padded_random_costs}")
        assignments_random, cost_random = find_minimum_cost_matching(padded_random_costs)

        actual_assignments = []
        actual_cost = 0
        print(f"Assignments (Row Index, Column Index in padded matrix):")
        for r,c in assignments_random:
            print(f"  Row {r} -> Padded Col {c}")
            if c < num_cols_random: # If not assigned to a dummy column
                actual_assignments.append((r,c))
                actual_cost += random_costs[r,c]
            else:
                print(f"  (Row {r} assigned to a dummy task)")
        print(f"Actual assignments to original columns: {actual_assignments}")
        print(f"Total Minimum Cost for Random Instance (to original columns): {actual_cost}")

# Example of a random square matrix
print("\n--- Random Square Instance Example ---")
size_random_sq = 4
random_costs_sq = np.random.randint(1, 50, size=(size_random_sq, size_random_sq))
print(f"Random Square Cost Matrix ({size_random_sq}x{size_random_sq}):\n{random_costs_sq}")
assignments_random_sq, cost_random_sq = find_minimum_cost_matching(random_costs_sq)
print(f"Assignments (Row Index, Column Index): {assignments_random_sq}")
print(f"Total Minimum Cost for Random Square Instance: {cost_random_sq}")