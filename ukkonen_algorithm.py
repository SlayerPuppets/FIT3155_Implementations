import matplotlib.pyplot as plt
import networkx as nx

class SuffixTreeNode:
    def __init__(self, start, end):
        # Mapping from character to child node.
        self.children = {}
        # For internal nodes, suffix_link points to another internal node.
        self.suffix_link = None
        # Edge label is represented as start and end indices (end can be a pointer for leaves).
        self.start = start  
        self.end = end      # For leaves, end is a mutable one-element list.
        # For further processing or debugging (e.g. storing suffix index).
        self.index = -1     

    def edge_length(self, current_pos):
        # Compute edge length. For leaves, end is a mutable pointer.
        if isinstance(self.end, list):
            return self.end[0] - self.start + 1
        return self.end - self.start + 1


class SuffixTree:
    def __init__(self, text):
        # Assume input text does not have a terminal symbol.
        # We build an implicit tree and later extend it explicitly.
        self.text = text  
        self.size = len(text)
        self.root = SuffixTreeNode(-1, -1)
        self.root.suffix_link = self.root  # Suffix link of root points to itself.
        
        # Active point components.
        self.active_node = self.root
        self.active_edge = -1  # Index in self.text (valid when active_length > 0).
        self.active_length = 0
        
        # Count of pending suffixes to be added in the current phase.
        self.remaining_suffix_count = 0
        
        # Global pointer for all leaves; leaves share this pointer.
        self.leaf_end = [-1]  # one-element list
        
        # Keeps track of the last created internal node in current extension.
        self.last_new_node = None

        # Build the implicit suffix tree (without the terminal symbol).
        self._build_suffix_tree()

    def _build_suffix_tree(self):
        # Process each phase by extending the tree with one additional character.
        for pos in range(self.size):
            self._extend_suffix_tree(pos)

    def _extend_suffix_tree(self, pos):
        # ********** Phase pos **********
        # Extend the tree with self.text[pos]
        self.leaf_end[0] = pos  # Rapid leaf extension update.
        self.remaining_suffix_count += 1
        self.last_new_node = None

        while self.remaining_suffix_count > 0:
            if self.active_length == 0:
                self.active_edge = pos

            current_char = self.text[self.active_edge]
            if current_char not in self.active_node.children:
                # Rule 2: Create a new leaf node.
                self.active_node.children[current_char] = SuffixTreeNode(pos, self.leaf_end)
                # Rule 3: If an internal node was created in the previous extension, set its suffix link.
                if self.last_new_node is not None:
                    self.last_new_node.suffix_link = self.active_node
                    self.last_new_node = None
            else:
                next_node = self.active_node.children[current_char]
                edge_length = next_node.edge_length(pos)
                if self.active_length >= edge_length:
                    # Skip/count trick: skip the entire edge.
                    self.active_edge += edge_length
                    self.active_length -= edge_length
                    self.active_node = next_node
                    continue

                # If the next character on the edge matches, do a premature stop.
                if self.text[next_node.start + self.active_length] == self.text[pos]:
                    if self.last_new_node is not None and self.active_node != self.root:
                        self.last_new_node.suffix_link = self.active_node
                        self.last_new_node = None
                    self.active_length += 1
                    break

                # Rule 2 (split edge): Split the edge and insert a new internal node.
                split_end = next_node.start + self.active_length - 1
                split_node = SuffixTreeNode(next_node.start, split_end)
                self.active_node.children[current_char] = split_node
                split_node.children[self.text[pos]] = SuffixTreeNode(pos, self.leaf_end)
                next_node.start += self.active_length
                split_node.children[self.text[next_node.start]] = next_node

                if self.last_new_node is not None:
                    self.last_new_node.suffix_link = split_node
                self.last_new_node = split_node

            self.remaining_suffix_count -= 1

            if self.active_node == self.root and self.active_length > 0:
                self.active_length -= 1
                self.active_edge = pos - self.remaining_suffix_count + 1
            elif self.active_node != self.root:
                self.active_node = self.active_node.suffix_link if self.active_node.suffix_link is not None else self.root

    def make_explicit(self):
        """
        Step 8: Extend the implicit suffix tree to an explicit suffix tree by adding
        a unique terminal symbol '$' and performing one final extension.
        """
        pos = self.size
        self.text += '$'
        self.size += 1
        self.leaf_end[0] = pos
        self.remaining_suffix_count += 1
        self.last_new_node = None
        self._extend_suffix_tree(pos)

    def set_suffix_index_by_dfs(self, node, label_length):
        """
        (Optional) DFS traversal to set the suffix index for each leaf.
        """
        if not node:
            return
        if len(node.children) == 0:
            node.index = self.size - label_length
            return
        for child in node.children.values():
            self.set_suffix_index_by_dfs(child, label_length + child.edge_length(self.leaf_end[0]))

    def _print_tree(self, node, indent=0):
        """
        (Optional) Utility method to print the suffix tree edges.
        """
        for child in node.children.values():
            end_index = child.end[0] if isinstance(child.end, list) else child.end
            edge_label = self.text[child.start: end_index + 1]
            print(' ' * indent + edge_label)
            self._print_tree(child, indent + 4)

    def visualize(self):
        """
        Visualization of the suffix tree using NetworkX and Matplotlib.
        Each node is assigned a unique ID. Edge labels show the substring (via start and end indices).
        """
        G = nx.DiGraph()
        node_labels = {}
        edge_labels = {}

        # DFS traversal to assign each node a unique id.
        next_id = 0
        def dfs(node):
            nonlocal next_id
            current_id = next_id
            next_id += 1
            # Label node with its id and, if a leaf, its suffix index.
            node_labels[current_id] = f"{current_id}" if node.index == -1 else f"{current_id}\n({node.index})"
            for child in node.children.values():
                child_id = dfs(child)
                if isinstance(child.end, list):
                    end_index = child.end[0]
                else:
                    end_index = child.end
                substring = self.text[child.start: end_index+1]
                G.add_edge(current_id, child_id)
                edge_labels[(current_id, child_id)] = substring
            return current_id

        dfs(self.root)

        # Try using Graphviz layout (requires pygraphviz/pydot); fallback to spring layout if not available.
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except Exception as e:
            pos = nx.spring_layout(G)
        
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=1500,
                node_color='lightblue', font_size=8, arrows=True)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)
        plt.title("Suffix Tree Visualization")
        plt.show()


# =========================
# Example Usage:
# =========================
if __name__ == '__main__':
    s = "banana"
    print("Building implicit suffix tree for:", s)
    st = SuffixTree(s)
    print("\nImplicit Suffix Tree (edge labels):")
    st._print_tree(st.root)

    # Extend the tree to be explicit.
    st.make_explicit()
    print("\nExplicit Suffix Tree (after adding '$'):")
    st._print_tree(st.root)

    # (Optional) Set suffix indices via DFS.
    st.set_suffix_index_by_dfs(st.root, 0)

    # Visualize the suffix tree.
    st.visualize()
