#!/usr/bin/env python3
import sys

def invert_bwt(bwt):
    n = len(bwt)
    # Compute rank for each character in bwt.
    # For each position i, ranks[i] is the number of occurrences of bwt[i]
    # seen so far (starting at 0).
    ranks = [0] * n
    count = {}  # count for each character
    for i, ch in enumerate(bwt):
        if ch not in count:
            count[ch] = 0
        ranks[i] = count[ch]
        count[ch] += 1

    # Build a dictionary first_occ that maps each character to its first occurrence in F.
    # F is the first column of the sorted rotations (i.e. sorted(bwt)).
    first_occ = {}
    total = 0
    for ch in sorted(count.keys()):
        first_occ[ch] = total
        total += count[ch]

    # Find the row that contains the terminal symbol "$".
    row = bwt.index('$')

    # Reconstruct the original text by following the LF mapping.
    # At each step, LF(row) = first_occ[bwt[row]] + ranks[row].
    # We do this n times (where n = len(bwt)) to recover all characters.
    result = []
    for i in range(n):
        ch = bwt[row]
        result.append(ch)
        row = first_occ[ch] + ranks[row]

    # The result is built in reverse (it ends at the terminal "$").
    # Reverse it to get the original string.
    original = ''.join(result[::-1])
    return original

def main():
    if len(sys.argv) < 2:
        print("Usage: {} inputfile".format(sys.argv[0]))
        sys.exit(1)

    input_filename = sys.argv[1]
    # Read the entire file and strip whitespace.
    with open(input_filename, 'r') as f:
        bwt = f.read().strip()

    original_text = invert_bwt(bwt)
    print("Inverted text:")
    print(original_text)

if __name__ == '__main__':
    main()
