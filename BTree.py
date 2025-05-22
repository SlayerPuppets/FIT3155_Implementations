from __future__ import annotations
from bisect import bisect_left
from typing import List, Optional, Tuple, Any, Iterable


class BTreeNode:
    """A single node in a B-tree."""
    def __init__(self, t: int, leaf: bool):
        self.t: int = t                   # minimum degree
        self.leaf: bool = leaf
        self.keys: List[Any] = []         # ordered keys
        self.children: List[BTreeNode] = []  # child pointers

    # ---------- search ----------
    def search(self, k) -> Optional["BTreeNode"]:
        i = bisect_left(self.keys, k)
        if i < len(self.keys) and self.keys[i] == k:
            return self
        return None if self.leaf else self.children[i].search(k)

    # ---------- split ----------
    def _split_child(self, i: int):
        """Split full child at index i; push median into self."""
        full = self.children[i]
        t = full.t
        median = full.keys[t - 1]

        # new right sibling
        right = BTreeNode(t, full.leaf)
        right.keys = full.keys[t:]                # ≥ t-1 keys
        full.keys = full.keys[: t - 1]            # ≥ t-1 keys

        if not full.leaf:                         # move pointers
            right.children = full.children[t:]
            full.children = full.children[: t]

        # insert median and right sibling into parent
        self.keys.insert(i, median)
        self.children.insert(i + 1, right)

    # ---------- insert ----------
    def insert_non_full(self, k):
        i = len(self.keys) - 1
        if self.leaf:
            self.keys.insert(bisect_left(self.keys, k), k)
            return

        # locate child; split if full on the way down
        i = bisect_left(self.keys, k)
        if len(self.children[i].keys) == 2 * self.t - 1:
            self._split_child(i)
            if k > self.keys[i]:
                i += 1
        self.children[i].insert_non_full(k)

    # ---------- delete helpers ----------
    def _merge(self, idx: int):
        """Merge child idx with child idx+1, pulling key down."""
        child, sibling = self.children[idx], self.children[idx + 1]
        t = self.t
        # bring separator down
        child.keys.append(self.keys.pop(idx))
        # absorb sibling’s keys & children
        child.keys.extend(sibling.keys)
        if not child.leaf:
            child.children.extend(sibling.children)
        self.children.pop(idx + 1)

    def _borrow_from_prev(self, idx: int):
        child, left = self.children[idx], self.children[idx - 1]
        t = self.t
        # shift separator into child
        child.keys.insert(0, self.keys[idx - 1])
        if not child.leaf:
            child.children.insert(0, left.children.pop())
        # move key from left up
        self.keys[idx - 1] = left.keys.pop()

    def _borrow_from_next(self, idx: int):
        child, right = self.children[idx], self.children[idx + 1]
        t = self.t
        child.keys.append(self.keys[idx])
        if not child.leaf:
            child.children.append(right.children.pop(0))
        self.keys[idx] = right.keys.pop(0)

    # main recursive delete
    def remove(self, k):
        idx = bisect_left(self.keys, k)

        # Case 1: key in this node
        if idx < len(self.keys) and self.keys[idx] == k:
            if self.leaf:                      # simple leaf removal
                self.keys.pop(idx)
            else:                              # internal-node cases
                if len(self.children[idx].keys) >= self.t:
                    pred = self._get_pred(idx)
                    self.keys[idx] = pred
                    self.children[idx].remove(pred)
                elif len(self.children[idx + 1].keys) >= self.t:
                    succ = self._get_succ(idx)
                    self.keys[idx] = succ
                    self.children[idx + 1].remove(succ)
                else:
                    self._merge(idx)
                    self.children[idx].remove(k)
            return

        # Case 2: key only in subtree
        if self.leaf:
            return  # not found
        # ensure child will have ≥ t keys
        if len(self.children[idx].keys) < self.t:
            self._fill(idx)
        # recurse into (possibly merged) child
        next_idx = idx if idx < len(self.children) else idx - 1
        self.children[next_idx].remove(k)

    # helper utilities
    def _get_pred(self, idx):  # right-most of left child
        cur = self.children[idx]
        while not cur.leaf:
            cur = cur.children[-1]
        return cur.keys[-1]

    def _get_succ(self, idx):  # left-most of right child
        cur = self.children[idx + 1]
        while not cur.leaf:
            cur = cur.children[0]
        return cur.keys[0]

    def _fill(self, idx):
        if idx > 0 and len(self.children[idx - 1].keys) >= self.t:
            self._borrow_from_prev(idx)
        elif idx < len(self.children) - 1 and len(self.children[idx + 1].keys) >= self.t:
            self._borrow_from_next(idx)
        else:
            merge_idx = idx - 1 if idx > 0 else idx
            self._merge(merge_idx)


class BTree:
    """Public wrapper around BTreeNode."""
    def __init__(self, t: int = 2):
        if t < 2:
            raise ValueError("B-tree degree must be ≥ 2")
        self.t = t
        self.root: Optional[BTreeNode] = None

    # -------- search --------
    def search(self, k):
        return None if self.root is None else self.root.search(k)

    # -------- insert --------
    def insert(self, k):
        if self.root is None:                 # empty tree
            self.root = BTreeNode(self.t, True)
            self.root.keys.append(k)
            return

        if len(self.root.keys) == 2 * self.t - 1:   # root full → split
            old_root = self.root
            self.root = BTreeNode(self.t, False)
            self.root.children.append(old_root)
            self.root._split_child(0)
            # choose side for new key
            idx = 0 if k < self.root.keys[0] else 1
            self.root.children[idx].insert_non_full(k)
        else:
            self.root.insert_non_full(k)

    # -------- delete --------
    def delete(self, k):
        if not self.root:
            return
        self.root.remove(k)
        if len(self.root.keys) == 0:        # shrink height
            self.root = self.root.children[0] if not self.root.leaf else None

    # -------- bulk load utility --------
    def build_from(self, iterable: Iterable[Any]):
        for x in iterable:
            self.insert(x)

    # pretty-print (for quick debugging)
    def _print(self, node=None, indent=0):
        node = node or self.root
        if node is None:
            print("(empty)")
            return
        print("  " * indent + str(node.keys))
        for c in node.children:
            self._print(c, indent + 1)


if __name__ == "__main__":
    t = 3
    b = BTree(t)
    for key in [20, 10, 30, 5, 15, 25, 35, 1, 6, 12]:
        b.insert(key)

    print("Initial:")
    b._print()

    print("\nSearch 15:", "found" if b.search(15) else "not found")

    b.delete(10)
    print("\nAfter deleting 10:")
    b._print()

    b.delete(1)
    b.delete(6)
    print("\nAfter deleting 1 and 6:")
    b._print()
