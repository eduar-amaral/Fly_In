from __future__ import annotations

from .heap_node import HeapNode


class HeapError(Exception):
    """Raised when the heap is used incorrectly."""


class MinHeap:
    """Minimal priority queue used by the Dijkstra search."""

    def __init__(self) -> None:
        """Create an empty min-heap."""
        self._data: list[HeapNode] = []

    def push(self, node: HeapNode) -> None:
        """Insert a node into the heap.

        Args:
            node: Heap node to insert.
        """
        self._data.append(node)

        self._bubble_up(len(self._data) - 1)

    def pop(self) -> HeapNode:
        """Remove and return the node with the smallest priority.

        Returns:
            The minimum-priority node.

        Raises:
            HeapError: If the heap is empty.
        """
        if not self._data:
            raise HeapError("pop from an empty heap")

        if len(self._data) == 1:
            return self._data.pop()

        root = self._data[0]
        self._data[0] = self._data.pop()

        self._sift_down(0)

        return root

    def peek(self) -> HeapNode:
        """Return the smallest node without removing it.

        Returns:
            The minimum-priority node.

        Raises:
            HeapError: If the heap is empty.
        """
        if not self._data:
            raise HeapError("peek at empty heap")

        return self._data[0]

    def is_empty(self) -> bool:
        """Return whether the heap contains any node."""
        return len(self._data) == 0

    def __len__(self) -> int:
        """Return the number of stored heap nodes."""
        return len(self._data)

    def _bubble_up(self, i: int) -> None:
        """Restore the min-heap invariant by moving a node upward."""
        while i > 0:
            parent = (i - 1) // 2

            if self._data[i].priority < self._data[parent].priority:
                self._data[i], self._data[parent] = (
                    self._data[parent],
                    self._data[i],
                )
                i = parent

            else:
                break

    def _sift_down(self, i: int) -> None:
        """Restore the min-heap invariant by moving a node downward."""
        n = len(self._data)

        while True:
            smallest = i

            left = 2 * i + 1
            right = 2 * i + 2

            if (
                left < n
                and self._data[left].priority
                < self._data[smallest].priority
            ):
                smallest = left

            if (
                right < n
                and self._data[right].priority
                < self._data[smallest].priority
            ):
                smallest = right

            if smallest == i:
                break

            self._data[i], self._data[smallest] = (
                self._data[smallest],
                self._data[i],
            )
            i = smallest

    def __repr__(self) -> str:
        """Return a compact debug representation of the heap."""
        if not self._data:
            return "MinHeap(empty)"

        return (
            f"MinHeap("
            f"min={self._data[0].priority}, "
            f"size={len(self._data)}"
            f")"
        )
