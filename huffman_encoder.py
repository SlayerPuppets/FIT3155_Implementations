#!/usr/bin/env python3
import sys
import heapq
from collections import Counter

def elias_gamma_encode(n):
    """
    Encodes a positive integer n (n ≥ 1) using Elias gamma coding.
    For a number n, let L be the number of bits in its binary representation.
    The code is (L-1) zeros followed by the L-bit binary representation.
    For example:
      n = 1  -> binary "1" (L=1)  -> output "1"
      n = 5  -> binary "101" (L=3) -> output "00" + "101" = "00101"
    """
    if n < 1:
        raise ValueError("Elias gamma encoding is only defined for positive integers")
    b = bin(n)[2:]
    L = len(b)
    return "0" * (L - 1) + b

class HuffmanNode:
    def __init__(self, freq, char=None, left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

def build_huffman_tree(freq_dict):
    """
    Builds a Huffman tree from freq_dict (a dictionary mapping characters to frequencies).
    Uses an increasing counter as a tie-breaker to guarantee a deterministic tree.
    """
    heap = []
    count = 0
    for char, f in freq_dict.items():
        heap.append((f, count, HuffmanNode(f, char)))
        count += 1
    heapq.heapify(heap)
    while len(heap) > 1:
        f1, count1, left = heapq.heappop(heap)
        f2, count2, right = heapq.heappop(heap)
        new_node = HuffmanNode(f1 + f2, None, left, right)
        heapq.heappush(heap, (new_node.freq, count, new_node))
        count += 1
    return heap[0][2]

def build_huffman_codes(node, prefix="", codebook=None):
    """
    Recursively builds a dictionary mapping each character to its Huffman code.
    """
    if codebook is None:
        codebook = {}
    if node.char is not None:
        codebook[node.char] = prefix or "0"
    else:
        build_huffman_codes(node.left, prefix + "0", codebook)
        build_huffman_codes(node.right, prefix + "1", codebook)
    return codebook

def text_to_bitstring(text, codebook):
    """
    Converts the text into a bit string by concatenating the Huffman code for each character.
    """
    return "".join(codebook[char] for char in text)

def pack_bits(bitstring):
    """
    Pads bitstring with zeros (if necessary) so its length is a multiple of 8, and packs it into bytes.
    """
    num_extra = (8 - len(bitstring) % 8) % 8
    bitstring += "0" * num_extra
    byte_array = bytearray()
    for i in range(0, len(bitstring), 8):
        byte_array.append(int(bitstring[i:i+8], 2))
    return bytes(byte_array)

def main():
    if len(sys.argv) != 3:
        print("Usage: python huffman_encoder.py input.txt output.bin")
        sys.exit(1)
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    
    # Read the input text and count character frequencies.
    with open(input_filename, "r", encoding="ascii") as infile:
        text = infile.read()
    freq = Counter(text)
    
    # Build the Huffman tree and codebook.
    huffman_tree = build_huffman_tree(freq)
    codebook = build_huffman_codes(huffman_tree)
    encoded_text = text_to_bitstring(text, codebook)
    
    # Build the header using Elias gamma coding.
    header = ""
    
    # (a) Write the number of unique characters.
    unique_chars = len(freq)
    header += elias_gamma_encode(unique_chars)
    
    # (b) For each distinct character—in the order of first appearance (Counter preserves insertion order):
    for char in freq:
        header += elias_gamma_encode(freq[char])
        header += format(ord(char), "08b")  # 8-bit ASCII code.
    
    # (c) Write the total number of characters.
    total_chars = len(text)
    header += elias_gamma_encode(total_chars)
    
    # (d) Append the Huffman-encoded payload.
    full_bitstring = header + encoded_text
    
    # Pack bits into bytes and write to the output file.
    output_bytes = pack_bits(full_bitstring)
    with open(output_filename, "wb") as outfile:
        outfile.write(output_bytes)
    
    print("Encoding complete.")
    print("Unique characters:", unique_chars)
    print("Huffman Codes:", codebook)

if __name__ == "__main__":
    main()
