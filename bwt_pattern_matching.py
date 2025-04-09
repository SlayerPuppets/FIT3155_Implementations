#!/usr/bin/env python3
import sys

def build_suffix_array(text):
    """
    Naïvely build a suffix array by sorting all suffixes.
    This has worst-case time complexity O(n^2 log n).
    """
    n = len(text)
    # Each suffix is identified by its starting index.
    sa = sorted(range(n), key=lambda i: text[i:])
    return sa

def build_bwt(text, sa):
    """
    Build the BWT using the suffix array.
    For each suffix starting at index i, the BWT character is text[i-1],
    with wrap-around for i = 0.
    """
    n = len(text)
    bwt_chars = []
    for i in range(n):
        pos = sa[i]
        bwt_chars.append(text[pos-1] if pos != 0 else text[-1])
    return ''.join(bwt_chars)

def build_occurrence_table(bwt):
    """
    Build an occurrence table for the BWT.
    For each character in the alphabet, occ_table[ch][j] gives the number of times
    ch appears in bwt[0:j] (j from 0 to n).
    Since the alphabet is fixed-size, this takes O(n) time.
    """
    n = len(bwt)
    # Determine alphabet from bwt
    alph = sorted(set(bwt))
    occ_table = {ch: [0]*(n+1) for ch in alph}
    for j in range(n):
        for ch in alph:
            occ_table[ch][j+1] = occ_table[ch][j]
        occ_table[bwt[j]][j+1] += 1
    return occ_table

def build_first_occurrence(bwt):
    """
    Build a dictionary that maps each character to its first occurrence index in F,
    the first column (i.e. sorted bwt).
    """
    alph = sorted(set(bwt))
    first_occ = {}
    total = 0
    for ch in alph:
        first_occ[ch] = total
        total += bwt.count(ch)
    return first_occ

def backward_search(bwt, pattern, occ_table, first_occ):
    """
    Perform backward search on the BWT.
    Processes the pattern from right to left to find the interval [sp, ep] in the BWT
    (and thus in the suffix array) corresponding to the pattern.
    Runs in O(m) time for pattern length m.
    Returns (sp, ep) or (-1, -1) if pattern is not found.
    """
    n = len(bwt)
    m = len(pattern)
    sp = 0
    ep = n - 1

    # Process pattern from rightmost to leftmost character.
    for i in range(m-1, -1, -1):
        ch = pattern[i]
        if ch not in first_occ:
            return -1, -1
        # Occurrence count up to sp (exclusive)
        sp = first_occ[ch] + occ_table[ch][sp]
        # Occurrence count up to ep (inclusive) 
        ep = first_occ[ch] + occ_table[ch][ep+1] - 1
        if sp > ep:
            return -1, -1
    return sp, ep

def main():
    if len(sys.argv) < 3:
        print("Usage: {} reference_file pattern_file".format(sys.argv[0]))
        sys.exit(1)
    
    ref_file = sys.argv[1]
    pattern_file = sys.argv[2]

    # Read reference text and pattern.
    with open(ref_file, 'r') as f:
        text = f.read().strip()
    with open(pattern_file, 'r') as f:
        pattern = f.read().strip()

    # Append unique terminal symbol if not present.
    if not text.endswith('$'):
        text += '$'

    # Construct the suffix array (naïve method).
    sa = build_suffix_array(text)
    # Construct the BWT from the suffix array.
    bwt = build_bwt(text, sa)

    # Build auxiliary data structures for backward search.
    occ_table = build_occurrence_table(bwt)
    first_occ = build_first_occurrence(bwt)

    # Perform backward search to find the interval for the pattern.
    sp, ep = backward_search(bwt, pattern, occ_table, first_occ)

    if sp == -1:
        print("Pattern not found in text.")
    else:
        # The suffix array interval [sp, ep] gives all occurrences of the pattern.
        print("Pattern found at positions:")
        for i in range(sp, ep+1):
            # Print the starting positions (1-indexed) from the suffix array.
            print(sa[i] + 1)

if __name__ == '__main__':
    main()
