import sys

# Compute the Bad Character Table (stores rightmost positions of each character in pattern)
def bad_character_table(pattern):
    table = {}
    for i, char in enumerate(pattern):
        table[char] = i  # Store rightmost occurrence of each character
    return table

# Z-algorithm to compute Z-array (useful for good suffix and matched prefix computation)
def z_algorithm(s):
    n = len(s)
    Z = [0] * n
    left, right = 0, 0
    for k in range(1, n):
        if k <= right:
            Z[k] = min(right - k + 1, Z[k - left])
        while k + Z[k] < n and s[Z[k]] == s[k + Z[k]]:
            Z[k] += 1
        if k + Z[k] - 1 > right:
            left, right = k, k + Z[k] - 1
    return Z

# Compute Good Suffix and Matched Prefix tables
def good_suffix_table(pattern):
    m = len(pattern)
    gs = [0] * (m + 1)  # Good suffix shift positions
    mp = [0] * (m + 1)  # Matched prefix lengths

    reversed_pattern = pattern[::-1]
    Z = z_algorithm(reversed_pattern)
    Z.reverse()  # Reverse to match original pattern positions

    # Populate Good Suffix table with boundary check
    for p in range(1, m):
        j = m - Z[p] + 1
        if j <= m:
            gs[j] = p

    # Populate Matched Prefix table
    longest = 0
    for i in range(m):
        if Z[i] == i + 1:
            longest = i + 1
        mp[m - i - 1] = longest

    return gs, mp

# Boyer-Moore main search function
def boyer_moore(text, pattern):
    n, m = len(text), len(pattern)
    positions = []  # Positions where pattern occurs

    # Preprocess pattern
    bad_char = bad_character_table(pattern)
    gs, mp = good_suffix_table(pattern)

    s = 0  # Current shift of the pattern over the text
    while s <= n - m:
        j = m - 1
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1
        if j < 0:  # Full pattern matched
            positions.append(s)
            shift = m - mp[1] if m > 1 else 1
            s += shift
        else:
            bc_shift = j - bad_char.get(text[s + j], -1)
            if gs[j + 1] > 0:
                gs_shift = m - gs[j + 1]
            else:
                gs_shift = m - mp[j + 1]
            s += max(bc_shift, gs_shift, 1)

    return positions

# Function to read contents from a file
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read().strip()

# Main function to run from command line, processing multiple patterns
def main():
    if len(sys.argv) != 3:
        print("Usage: python boyer_moore.py <text_file> <pattern_file>")
        sys.exit(1)

    text_file, pattern_file = sys.argv[1], sys.argv[2]
    text = read_file(text_file)

    # Process each pattern line separately
    with open(pattern_file, 'r', encoding='utf-8') as pf:
        patterns = [line.strip() for line in pf if line.strip()]

    for pattern in patterns:
        positions = boyer_moore(text, pattern)
        print(f"Pattern '{pattern}' found at positions:", positions)

if __name__ == "__main__":
    main()