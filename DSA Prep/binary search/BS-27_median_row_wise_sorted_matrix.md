# BS-27 — Median in a Row-Wise Sorted Matrix

**Playlist:** [takeUforward BS-27](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an `n x m` matrix `mat` where:

- `n` and `m` are both **odd** (so `n * m` is odd, and a unique median exists)
- every **row** is sorted in non-decreasing order
- there is no order between rows

The median is the element that would sit in the middle if you flattened and sorted the whole matrix (0-based middle index `(n*m) // 2`).

Return that median. Do **not** flatten the matrix into an array of size `n*m` if you can avoid O(n m log(n m)) extra memory.

**Examples**

- `mat = [[1, 3, 5], [2, 6, 9], [3, 6, 9]]` → `5`  
  Sorted flatten: `1, 2, 3, 3, 5, 6, 6, 9, 9`
- `mat = [[1, 3, 5], [2, 6, 9], [3, 6, 9]]` middle index `4` is `5`

**Constraints:** `1 <= n, m <= 400` typical, odd dimensions.

## Approaches

**1. Brute force**  
Copy all `n * m` values, sort, pick the middle.  
Time: O(n m log(n m)) · Space: O(n m)

**2. Optimized — binary search on the value**  
The median is the smallest number `x` such that at least `(n*m)//2 + 1` elements are `<= x`. Search `x` between the global min (`min of first column`) and global max (`max of last column`). For a candidate `mid`, count how many entries are `<= mid` by running upper bound in each row.  
Time: O(n log m · log(max - min)) · Space: O(1)

## Pseudocode (optimized)

```
median_matrix(mat):
    low ← min of first column
    high ← max of last column
    need ← (n * m) / 2          # number of elements strictly before the median

    count_leq(x):
        return sum over rows of upper_bound(row, x)

    while low ≤ high:
        mid ← low + (high - low) / 2
        if count_leq(mid) ≤ need:
            low ← mid + 1
        else:
            high ← mid - 1
    return low
```

## Solution (optimized)

```python
from typing import List


def upper_bound(nums: List[int], x: int) -> int:
    low, high, ans = 0, len(nums) - 1, len(nums)
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] > x:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans


def median_row_wise_sorted(mat: List[List[int]]) -> int:
    n, m = len(mat), len(mat[0])
    low = min(row[0] for row in mat)
    high = max(row[-1] for row in mat)
    need = (n * m) // 2

    def count_leq(x: int) -> int:
        return sum(upper_bound(row, x) for row in mat)

    while low <= high:
        mid = low + (high - low) // 2
        if count_leq(mid) <= need:
            low = mid + 1
        else:
            high = mid - 1
    return low
```
