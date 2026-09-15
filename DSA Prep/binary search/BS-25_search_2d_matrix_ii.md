# BS-25 — Search in a 2D Matrix II

**Playlist:** [takeUforward BS-25](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an `n x m` matrix where:

- each **row** is sorted left to right
- each **column** is sorted top to bottom

There is **no** guarantee that the next row starts after the previous row’s last value (unlike BS-24). Integers may also repeat.

Given `target`, return `true` if it exists, else `false`.

**Examples**

```
matrix = [
  [1,  4,  7, 11, 15],
  [2,  5,  8, 12, 19],
  [3,  6,  9, 16, 22],
  [10, 13, 14, 17, 24],
  [18, 21, 23, 26, 30]
]
```

- `target = 5` → `true`
- `target = 20` → `false`

**Constraints:** `1 <= n, m <= 300` typical.

## Approaches

**1. Brute force**  
Scan every cell.  
Time: O(n · m)

**2. Better**  
Binary search each row (or each column).  
Time: O(n log m)

**3. Optimized — staircase from the top-right**  
Start at `(0, m-1)`. If the value is `target`, return true. If it is larger than `target`, move left (the rest of the column is even larger). If it is smaller, move down (the rest of the row is even smaller). Each step drops a row or a column.  
Time: O(n + m) · Space: O(1)

## Pseudocode (optimized)

```
search_matrix_ii(matrix, target):
    row ← 0, col ← m - 1
    while row < n and col ≥ 0:
        val ← matrix[row][col]
        if val = target: return true
        if val > target: col ← col - 1
        else: row ← row + 1
    return false
```

## Solution (optimized)

```python
from typing import List


def search_matrix_ii(matrix: List[List[int]], target: int) -> bool:
    n, m = len(matrix), len(matrix[0])
    row, col = 0, m - 1
    while row < n and col >= 0:
        val = matrix[row][col]
        if val == target:
            return True
        if val > target:
            col -= 1
        else:
            row += 1
    return False
```
