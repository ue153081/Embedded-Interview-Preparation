# BS-23 — Row With Maximum Number of 1s (Binary Search on 2D)

**Playlist:** [takeUforward BS-23](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an `n x m` binary matrix `mat`. Every row is sorted (all `0`s appear before all `1`s).

Return the **0-based index** of the row that contains the **maximum number of 1s**. If several rows share that maximum, return the **smallest** index. If the matrix contains no `1`s, return `-1`.

**Examples**

- `mat = [[0, 0, 1], [0, 1, 1], [0, 0, 0]]` → `1` (two 1s)
- `mat = [[0, 0], [0, 0]]` → `-1`

**Constraints:** `1 <= n, m <= 10^3` typical; each row sorted.

## Approaches

**1. Brute force**  
Count 1s in every row.  
Time: O(n · m) · Space: O(1)

**2. Optimized — lower bound of 1 in each row**  
Because a row is sorted, the first `1` is `lower_bound(row, 1)`. The number of 1s is `m - that_index`. Track the best row.  
Time: O(n log m) · Space: O(1)

(You can also walk from the top-right in O(n + m); the log-per-row method is the 2D binary-search intro.)

## Pseudocode (optimized)

```
row_with_max_ones(mat):
    best_row ← -1, best_count ← 0
    for i ← 0 .. n - 1:
        first_one ← lower_bound(mat[i], 1)
        count ← m - first_one
        if count > best_count:
            best_count ← count
            best_row ← i
    return best_row if best_count > 0 else -1
```

## Solution (optimized)

```python
from typing import List


def lower_bound(nums: List[int], x: int) -> int:
    low, high, ans = 0, len(nums) - 1, len(nums)
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] >= x:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans


def row_with_max_ones(mat: List[List[int]]) -> int:
    n = len(mat)
    m = len(mat[0]) if n else 0
    best_row, best_count = -1, 0
    for i, row in enumerate(mat):
        count = m - lower_bound(row, 1)
        if count > best_count:
            best_count = count
            best_row = i
    return best_row if best_count else -1
```
