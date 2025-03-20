def compute_z(s):
    n = len(s)
    if n == 0:
        return []
    Z = [0] * n
    Z[0] = n  # The entire string is the prefix itself
    l, r = 0, 0  # Window [l, r) that matches the prefix
    
    for i in range(1, n):
        # Case 1: Current index i is outside the current window
        if i > r:
            l = r = i
            # Expand the window as long as characters match
            while r < n and s[r - l] == s[r]:
                r += 1
            Z[i] = r - l  # Length of the match
            r -= 1  # Adjust r back to the end of the matched window
        else:
            k = i - l  # Corresponding index in the prefix
            # Case 2: The precomputed value is within the remaining window
            if Z[k] < r - i + 1:
                Z[i] = Z[k]
            # Case 3: Need to expand the window starting from i
            else:
                l = i  # Move the left end of the window to i
                while r < n and s[r - l] == s[r]:
                    r += 1
                Z[i] = r - l
                r -= 1  # Adjust r back after expansion
    return Z

# Example usage
s = "ababa"
print(compute_z(s))  # Output: [5, 0, 3, 0, 1]