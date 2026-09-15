# BS-24 — Search in a 2D Matrix I

**Playlist:** [takeUforward BS-24](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an `n x m` integer matrix with these properties:

- each row is sorted left to right
- the first integer of each row is **greater than** the last integer of the previous row

(The matrix is a single increasing sequence if you flatten it row by row.)

Given `target`, return `true` if it exists in the matrix, otherwise `false`. Aim for O(log(n · m)) time.

**Examples**

- `matrix = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]`, `target = 3` → `true`
- same matrix, `target = 13` → `false`

**Constraints:** `1 <= n, m <= 100` on LeetCode; treat general `n, m` in interviews.

## Approaches

**1. Brute force**  
Scan every cell.  
Time: O(n · m) · Space: O(1)

**2. Better**  
Binary search each row, or binary-search the row then the column.  
Time: O(n log m) or O(log n + log m)

**3. Optimized — treat as a 1D sorted array**  
Index `mid` in `[0, n*m - 1]` maps to cell `(mid // m, mid % m)`. Standard binary search.  
Time: O(log(n · m)) · Space: O(1)

## Pseudocode (optimized)

```
search_matrix(matrix, target):
    n ← rows, m ← cols
    low ← 0, high ← n * m - 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        val ← matrix[mid / m][mid % m]
        if val = target: return true
        if val < target: low ← mid + 1
        else: high ← mid - 1
    return false
```

## Solution (optimized)

```python
from typing import List


def search_matrix(matrix: List[List[int]], target: int) -> bool:
    n, m = len(matrix), len(matrix[0])
    low, high = 0, n * m - 1
    while low <= high:
        mid = low + (high - low) // 2
        val = matrix[mid // m][mid % m]
        if val == target:
            return True
        if val < target:
            low = mid + 1
        else:
            high = mid - 1
    return False
```
