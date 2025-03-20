def compute_Z(S):
    """
    Compute the Z-array for string S using the Z-algorithm.
    
    Parameters:
    S (str): The input string.

    Returns:
    list: The Z-array where Z[i] gives the longest substring starting at S[i] 
          that matches the prefix of S.
    """
    n = len(S)
    Z = [0] * n
    l, r = 0, 0  # Left and right boundaries of the Z-box

    for i in range(1, n):
        if i <= r:  # Case 2: Inside a Z-box
            k = i - l
            Z[i] = min(r - i + 1, Z[k])  # Use previously computed Z-values
        
        while i + Z[i] < n and S[Z[i]] == S[i + Z[i]]:  # Explicit comparison
            Z[i] += 1
        
        if i + Z[i] - 1 > r:  # Update Z-box boundaries
            l, r = i, i + Z[i] - 1
    
    return Z


def pattern_matching_Z(text, pattern):
    """
    Find all occurrences of pattern in text using the Z-algorithm.
    
    Parameters:
    text (str): The main text.
    pattern (str): The pattern to search.

    Returns:
    list: A list of starting positions in the text where the pattern is found.
    """
    # Step 1: Concatenate pattern and text with a unique delimiter "&"
    concat_str = pattern + "&" + text
    
    # Step 2: Compute the Z-array
    Z = compute_Z(concat_str)
    
    # Step 3: Find pattern matches in the text
    pattern_length = len(pattern)
    matches = []
    
    for i in range(pattern_length + 1, len(concat_str)):
        if Z[i] == pattern_length:  # A full match occurs
            matches.append(i - pattern_length - 1)  # Adjust index to text
    
    return matches


# Example usage
text = "ababcababc"
pattern = "abc"
matches = pattern_matching_Z(text, pattern)
print("Pattern found at positions:", matches)
