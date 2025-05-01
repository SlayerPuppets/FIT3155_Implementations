from __future__ import annotations
from typing import Any, Generator, Optional


class FibonacciNode:
    """A node inside a Fibonacci Heap."""

    __slots__ = (
        "key",
        "value",
        "degree",
        "mark",
        "parent",
        "child",
        "left",
        "right",
    )

    def __init__(self, key: float, value: Any = None):
        self.key: float = key
        self.value: Any = value
        self.degree: int = 0
        self.mark: bool = False
        self.parent: Optional[FibonacciNode] = None
        self.child: Optional[FibonacciNode] = None
        # a node in a circular doubly‑linked list points to itself initially
        self.left: FibonacciNode = self
        self.right: FibonacciNode = self

    # Helper methods ---------------------------------------------------------

    def _iterate(start: Optional["FibonacciNode"]) -> Generator["FibonacciNode", None, None]:
        """Generator that iterates over a circular doubly linked list of nodes."""
        if start is None:
            return
        node = stop = start
        flag = False
        while True:
            if node is stop and flag:
                break
            flag = True
            yield node
            node = node.right

    # Debug ------------------------------------------------------------------

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Node key={self.key} degree={self.degree} mark={self.mark} "
            f"parent={None if self.parent is None else self.parent.key}>"
        )


class FibonacciHeap:
    """Min‑priority Fibonacci Heap implementation supporting insert, min, merge,
    extract‑min, decrease‑key, and delete operations (amortised)."""

    def __init__(self):
        self.min_node: Optional[FibonacciNode] = None
        self.total_nodes: int = 0

    # ---------------------------------------------------------------------
    # Core public API
    # ---------------------------------------------------------------------

    def insert(self, key: float, value: Any = None) -> FibonacciNode:
        node = FibonacciNode(key, value)
        self._merge_with_root_list(node)
        if self.min_node is None or node.key < self.min_node.key:
            self.min_node = node
        self.total_nodes += 1
        return node

    def merge(self, other: "FibonacciHeap") -> "FibonacciHeap":
        """O(1) meld of two heaps. Leaves `other` empty."""
        if other.min_node is None:
            return self
        if self.min_node is None:
            self.min_node = other.min_node
            self.total_nodes = other.total_nodes
            other._reset()
            return self
        # concatenate root lists
        self._concatenate_root_lists(other.min_node, self.min_node)
        if other.min_node.key < self.min_node.key:
            self.min_node = other.min_node
        self.total_nodes += other.total_nodes
        other._reset()
        return self

    def find_min(self) -> Optional[FibonacciNode]:
        return self.min_node

    def extract_min(self) -> Optional[FibonacciNode]:
        z = self.min_node
        if z is not None:
            # promote children of z to root list
            if z.child is not None:
                for child in FibonacciNode._iterate(z.child):
                    child.parent = None
                    self._merge_with_root_list(child)
            # remove z from root list
            self._remove_from_root_list(z)
            if z is z.right:  # single node left
                self.min_node = None
            else:
                self.min_node = z.right
                self._consolidate()
            self.total_nodes -= 1
        return z

    def decrease_key(self, x: FibonacciNode, k: float) -> None:
        if k > x.key:
            raise ValueError("new key is greater than current key")
        x.key = k
        y = x.parent
        if y is not None and x.key < y.key:
            self._cut(x, y)
            self._cascading_cut(y)
        if self.min_node is None or x.key < self.min_node.key:
            self.min_node = x

    def delete(self, x: FibonacciNode) -> None:
        self.decrease_key(x, float("-inf"))
        self.extract_min()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _merge_with_root_list(self, node: FibonacciNode) -> None:
        if self.min_node is None:
            self.min_node = node
        else:
            # insert node to the left of min_node
            self._concatenate_root_lists(node, self.min_node)

    @staticmethod
    def _concatenate_root_lists(a: FibonacciNode, b: FibonacciNode) -> None:
        """Splice circular lists headed by a and b (before: a<->..., b<->...)."""
        a_left = a.left
        b_left = b.left
        a.left = b_left
        b_left.right = a
        b.left = a_left
        a_left.right = b

    def _remove_from_root_list(self, node: FibonacciNode) -> None:
        if node.right is node:
            return  # single element list
        node.left.right = node.right
        node.right.left = node.left

    # -------------------- consolidate -----------------------------------

    def _consolidate(self) -> None:
        import math

        array_size = int(math.log(self.total_nodes, 1.61803398875)) + 2 if self.total_nodes > 0 else 1
        A: list[Optional[FibonacciNode]] = [None] * array_size
        # list of roots to process (detached iteration because we'll modify list)
        roots = [x for x in FibonacciNode._iterate(self.min_node)]
        for w in roots:
            x = w
            d = x.degree
            while A[d] is not None:
                y = A[d]
                if x.key > y.key:
                    x, y = y, x  # ensure x.key <= y.key
                self._link(y, x)
                A[d] = None
                d += 1
            A[d] = x
        # rebuild root list and find new min
        self.min_node = None
        for node in A:
            if node is not None:
                # isolate node circular list to itself before merging
                node.left = node.right = node
                self._merge_with_root_list(node)
                if self.min_node is None or node.key < self.min_node.key:
                    self.min_node = node

    def _link(self, y: FibonacciNode, x: FibonacciNode) -> None:
        """Make y a child of x."""
        # remove y from root list
        self._remove_from_root_list(y)
        # make y child of x
        y.left = y.right = y
        if x.child is None:
            x.child = y
        else:
            self._concatenate_root_lists(y, x.child)
        y.parent = x
        x.degree += 1
        y.mark = False

    # --------------------- cuts -----------------------------------------

    def _cut(self, x: FibonacciNode, y: FibonacciNode) -> None:
        """Detach x from y's child list and move to root list."""
        # remove x from child list of y
        if y.child is x:
            if x.right is x:
                y.child = None
            else:
                y.child = x.right
        x.left.right = x.right
        x.right.left = x.left
        y.degree -= 1
        # add x to root list
        x.left = x.right = x
        self._merge_with_root_list(x)
        x.parent = None
        x.mark = False

    def _cascading_cut(self, y: FibonacciNode) -> None:
        z = y.parent
        if z is not None:
            if not y.mark:
                y.mark = True
            else:
                self._cut(y, z)
                self._cascading_cut(z)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return self.total_nodes

    def _reset(self) -> None:
        """Reset heap to empty (used after merge)."""
        self.min_node = None
        self.total_nodes = 0

    # For debugging / representation -----------------------------------

    def _iter_roots(self):
        return FibonacciNode._iterate(self.min_node)

    def __repr__(self) -> str:  # pragma: no cover
        if self.min_node is None:
            return "<FibonacciHeap empty>"
        roots = ", ".join(str(n.key) for n in self._iter_roots())
        return f"<FibonacciHeap min={self.min_node.key} roots=[{roots}] size={self.total_nodes}>"
