#!/usr/bin/env python3
import sys

def construct_bwt(text):
    # Ensure the text ends with a unique terminal symbol.
    if not text.endswith('$'):
        text += '$'
    n = len(text)
    
    # Generate all cyclic rotations of text.
    # Each rotation is text[i:] + text[:i] for 0 <= i < n.
    rotations = [text[i:] + text[:i] for i in range(n)]
    
    # Sort the rotations lexicographically.
    rotations.sort()
    
    # The BWT is the last character of each rotation in the sorted list.
    bwt = ''.join(rotation[-1] for rotation in rotations)
    return bwt

def main():
    if len(sys.argv) < 2:
        print("Usage: {} inputfile".format(sys.argv[0]))
        sys.exit(1)

    input_filename = sys.argv[1]
    
    # Read the entire file and strip any extra whitespace.
    with open(input_filename, 'r') as f:
        text = f.read().strip()
    
    bwt = construct_bwt(text)
    
    # Output the original text and its BWT.
    print("Input text:", text)
    print("BWT:", bwt)

if __name__ == '__main__':
    main()
