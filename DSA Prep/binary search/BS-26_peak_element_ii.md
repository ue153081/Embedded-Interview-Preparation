# BS-26 — Find Peak Element II

**Playlist:** [takeUforward BS-26](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an `n x m` matrix `mat` of **distinct** integers. A **peak** is a cell strictly greater than its four adjacent neighbors (up, down, left, right). Cells outside the matrix are treated as `-1`.

Return the `[row, col]` of **any** peak. You should use O(n log m) time (or O(m log n)), not a full scan of every cell in the worst-case interview target.

**Examples**

- `mat = [[1, 4], [3, 2]]` → `[0, 1]` (value `4`) or `[1, 0]` (value `3`)
- `mat = [[10, 20, 15], [21, 30, 14], [7, 16, 32]]` → `[1, 1]` (`30`) or `[2, 2]` (`32`)

**Constraints:** `1 <= n, m <= 500`, all values unique and positive.

## Approaches

**1. Brute force**  
Check every cell against its neighbors.  
Time: O(n · m)

**2. Optimized — binary search on columns**  
Take the middle column, find its **maximum** cell. Compare that cell to left and right neighbors. If it is a peak, return it. If the left neighbor is larger, a peak exists on the left half (you can only “climb” that way); otherwise search the right half.  
Time: O(n log m) · Space: O(1)

## Pseudocode (optimized)

```
find_peak_grid(mat):
    low ← 0, high ← m - 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        row ← index of max in column mid
        left ← mat[row][mid - 1] or -1
        right ← mat[row][mid + 1] or -1
        if mat[row][mid] ≥ left and mat[row][mid] ≥ right:
            return [row, mid]
        if left > mat[row][mid]:
            high ← mid - 1
        else:
            low ← mid + 1
```

## Solution (optimized)

```python
from typing import List


def find_peak_grid(mat: List[List[int]]) -> List[int]:
    n, m = len(mat), len(mat[0])
    low, high = 0, m - 1

    def max_in_col(c: int) -> int:
        r = 0
        for i in range(1, n):
            if mat[i][c] > mat[r][c]:
                r = i
        return r

    while low <= high:
        mid = low + (high - low) // 2
        row = max_in_col(mid)
        left = mat[row][mid - 1] if mid - 1 >= 0 else -1
        right = mat[row][mid + 1] if mid + 1 < m else -1
        if mat[row][mid] >= left and mat[row][mid] >= right:
            return [row, mid]
        if left > mat[row][mid]:
            high = mid - 1
        else:
            low = mid + 1
    return [-1, -1]
```
