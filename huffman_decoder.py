#!/usr/bin/env python3
import sys
import heapq

def elias_gamma_decode(bitstr, pos):
    """
    Decodes an Elias gamma–encoded positive integer from bitstr starting at position pos.
    Returns a tuple (value, new_pos).
    """
    zeros = 0
    while pos < len(bitstr) and bitstr[pos] == '0':
        zeros += 1
        pos += 1
    if pos + zeros > len(bitstr):
        raise ValueError("Incomplete Elias gamma code in bitstream")
    binary_value = bitstr[pos: pos + zeros + 1]
    value = int(binary_value, 2)
    pos += zeros + 1
    return value, pos

class HuffmanNode:
    def __init__(self, freq, char=None, left=None, right=None):
        self.freq = freq
        self.char = char
        self.left = left
        self.right = right

def build_huffman_tree(freq_dict):
    """
    Builds the Huffman tree from the frequency dictionary.
    Uses an increasing counter as a tie-breaker to ensure determinism.
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

def decode_payload(bitstr, pos, root, total_chars):
    """
    Decodes the Huffman-encoded payload starting at bitstr[pos] using the Huffman tree.
    Stops when total_chars characters have been decoded.
    """
    decoded_chars = []
    node = root
    while len(decoded_chars) < total_chars and pos < len(bitstr):
        bit = bitstr[pos]
        pos += 1
        if bit == '0':
            node = node.left
        else:
            node = node.right
        if node is None:
            break  # Likely reached padding.
        if node.char is not None:
            decoded_chars.append(node.char)
            node = root
    if len(decoded_chars) != total_chars:
        raise ValueError("Decoded character count does not match expected total. " +
                         f"Expected {total_chars}, got {len(decoded_chars)}.")
    return "".join(decoded_chars), pos

def unpack_bytes(byte_data):
    """
    Converts byte_data (a bytes object) to a string of bits.
    """
    bits = ""
    for byte in byte_data:
        bits += format(byte, "08b")
    return bits

def main():
    if len(sys.argv) != 3:
        print("Usage: python huffman_decoder.py input.bin output.txt")
        sys.exit(1)
    
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    
    # Read the binary file and convert it to a bit string.
    with open(input_filename, "rb") as infile:
        byte_data = infile.read()
    bitstr = unpack_bytes(byte_data)
    
    pos = 0
    # (a) Decode the number of unique characters.
    num_unique, pos = elias_gamma_decode(bitstr, pos)
    
    # (b) For each unique character, decode frequency and then read 8 bits for the ASCII code.
    freq_dict = {}
    for _ in range(num_unique):
        freq, pos = elias_gamma_decode(bitstr, pos)
        ascii_code = bitstr[pos: pos+8]
        pos += 8
        char = chr(int(ascii_code, 2))
        freq_dict[char] = freq
    # (c) Decode the total number of characters.
    total_chars, pos = elias_gamma_decode(bitstr, pos)
    
    # Rebuild the Huffman tree.
    huffman_root = build_huffman_tree(freq_dict)
    
    # Decode the payload.
    decoded_text, pos = decode_payload(bitstr, pos, huffman_root, total_chars)
    
    with open(output_filename, "w", encoding="ascii") as outfile:
        outfile.write(decoded_text)
    
    print("Decoding complete.")
    print("Unique characters:", num_unique)
    print("Frequencies:", freq_dict)
    print("Total characters:", total_chars)

if __name__ == "__main__":
    main()
