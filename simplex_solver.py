import numpy as np

def simplex_solver(c, A, b):
    """
    Solves a canonical linear programming problem (Maximization, all <= constraints)
    using the simplex tableau method.

    Args:
        c (list or np.array): Coefficients of the objective function.
        A (list of lists or np.array): Matrix of coefficients for constraint inequalities.
        b (list or np.array): Vector of RHS values for constraint inequalities.

    Returns:
        tuple: (max_obj_value, solution_vars, status_message)
               - max_obj_value (float): The maximized objective function value.
               - solution_vars (np.array): Values of the decision variables.
               - status_message (str): "Optimal", "Unbounded", or "Max iterations reached".
               Returns (None, None, message) if not optimal.
    """
    num_decision_vars = len(c)
    num_constraints = len(A)

    # Convert inputs to numpy arrays
    c = np.array(c, dtype=float)
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)

    # Create the initial simplex tableau
    # Columns: decision_vars | slack_vars | RHS
    # Rows: constraints | objective_function
    tableau = np.zeros((num_constraints + 1, num_decision_vars + num_constraints + 1))

    # Fill constraint coefficients (A matrix part)
    tableau[:num_constraints, :num_decision_vars] = A

    # Fill slack variable coefficients (identity matrix for slacks)
    for i in range(num_constraints):
        tableau[i, num_decision_vars + i] = 1.0

    # Fill RHS of constraints
    tableau[:num_constraints, -1] = b

    # Fill objective function row (-c for maximization)
    tableau[-1, :num_decision_vars] = -c
    # tableau[-1, -1] is initially 0 (Z = 0)

    # Keep track of which variable (by column index) is basic in each row
    # Initial basic variables are the slack variables
    # Column indices:
    # 0 to num_decision_vars-1 : decision variables
    # num_decision_vars to num_decision_vars+num_constraints-1 : slack variables
    basic_variables_indices = list(range(num_decision_vars, num_decision_vars + num_constraints))

    iteration = 0
    max_iterations = 100  # Safety break for potential cycling or very large problems

    while iteration < max_iterations:
        iteration += 1

        # Check for optimality: all coefficients in obj_row (excluding RHS) >= 0
        obj_row_coeffs = tableau[-1, :-1]
        if np.all(obj_row_coeffs >= -1e-9):  # Use tolerance for float comparison
            break  # Optimal solution found

        # Select pivot column: most negative coefficient in objective row
        pivot_col_idx = np.argmin(obj_row_coeffs)
        if obj_row_coeffs[pivot_col_idx] >= -1e-9: # Should be caught by above, but safety
            break # Optimal

        # Select pivot row: minimum non-negative ratio test
        ratios = np.full(num_constraints, np.inf) # Initialize ratios to infinity
        pivot_column_values = tableau[:num_constraints, pivot_col_idx]

        for i in range(num_constraints):
            if pivot_column_values[i] > 1e-9:  # Denominator must be strictly positive
                ratios[i] = tableau[i, -1] / pivot_column_values[i]
            # else: ratios[i] remains np.inf (or can be set explicitly)

        pivot_row_idx = np.argmin(ratios)

        if ratios[pivot_row_idx] == np.inf : # or np.isinf(ratios[pivot_row_idx])
            return None, None, "Unbounded: No valid pivot row found."

        pivot_element = tableau[pivot_row_idx, pivot_col_idx]

        # Perform pivot operation
        # 1. Normalize pivot row (divide by pivot_element to make pivot_element 1)
        tableau[pivot_row_idx, :] /= pivot_element

        # 2. Make other elements in pivot column zero
        for i in range(num_constraints + 1):  # Iterate through all rows including objective row
            if i != pivot_row_idx:
                factor = tableau[i, pivot_col_idx]
                tableau[i, :] -= factor * tableau[pivot_row_idx, :]

        # Update the basic variable for the pivot row
        basic_variables_indices[pivot_row_idx] = pivot_col_idx
    else: # Loop finished due to max_iterations
        return None, None, "Max iterations reached. Solution might not be optimal."

    # Extract solution
    max_obj_value = tableau[-1, -1]
    solution_vars = np.zeros(num_decision_vars)

    for i in range(num_constraints):
        basic_var_col_idx = basic_variables_indices[i]
        # If the basic variable in this row is one of the original decision variables
        if basic_var_col_idx < num_decision_vars:
            solution_vars[basic_var_col_idx] = tableau[i, -1]

    # Final check on optimality status if loop broke early due to non-negative obj_row
    if np.all(tableau[-1, :-1] >= -1e-9):
        status_message = "Optimal"
    else: # Should not happen if max_iterations not reached, but as a fallback
        status_message = "Suboptimal (check iterations or problem formulation)"


    return max_obj_value, solution_vars, status_message


# Inputs for Question 1
c_q1 = [1, 2]
A_q1 = [
    [4, 1],
    [3, 2],
    [2, 3],
    [0, 1],
    [-1, 1]
]
b_q1 = [44, 39, 37, 9, 6]

# Solve the linear program
max_value_q1, solution_variables_q1, status_q1 = simplex_solver(c_q1, A_q1, b_q1)

# Output the results
print("--- Solution for Question 1 ---")
print(f"Status: {status_q1}")
if status_q1 == "Optimal":
    print(f"Maximized objective function value (Z): {max_value_q1:.5f}")
    decision_var_names = ['x', 'y'] # Assuming x and y for Question 1
    print("Values of the decision variables:")
    for i in range(len(solution_variables_q1)):
        print(f"  {decision_var_names[i]}: {solution_variables_q1[i]:.5f}")
elif max_value_q1 is not None: # For cases like "Max iterations reached" but still gives a result
    print(f"Objective function value (Z): {max_value_q1:.5f}")
    decision_var_names = ['x', 'y']
    print("Values of the decision variables (possibly suboptimal):")
    for i in range(len(solution_variables_q1)):
        print(f"  {decision_var_names[i]}: {solution_variables_q1[i]:.5f}")
else:
    print("No solution found or problem is unbounded.")