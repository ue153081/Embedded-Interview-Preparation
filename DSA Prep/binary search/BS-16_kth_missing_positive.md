# BS-16 — Kth Missing Positive Number

**Playlist:** [takeUforward BS-16](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given a **strictly increasing** array `arr` of positive integers (starting from values ≥ 1, not necessarily containing 1). Some positive integers are missing from the array.

Return the `k`th missing positive integer.

**Examples**

- `arr = [2, 3, 4, 7, 11]`, `k = 5` → `9`  
  Missing: `1, 5, 6, 8, 9, ...`
- `arr = [1, 2, 3, 4]`, `k = 2` → `6`

**Constraints:** `1 <= n <= 10^5`, `1 <= k <= 10^9`.

## Approaches

**1. Brute force**  
Walk from `1` upward, skip values that appear in `arr`, until you have skipped `k` missing numbers.  
Time: O(n + k) · Space: O(1) (or O(n) with a set)

**2. Optimized — binary search on how many are missing**  
At index `i` (0-based), the count of missing numbers before `arr[i]` is `arr[i] - (i + 1)`. Find the rightmost index where this count is still `< k`. Then the answer is `low + k` (equivalently `arr[high] + (k - missing[high])` after the loop).  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
find_kth_missing(arr, k):
    low ← 0, high ← n - 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        missing ← arr[mid] - (mid + 1)
        if missing < k:
            low ← mid + 1
        else:
            high ← mid - 1
    return low + k
```

## Solution (optimized)

```python
from typing import List


def find_kth_missing(arr: List[int], k: int) -> int:
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = low + (high - low) // 2
        missing = arr[mid] - (mid + 1)
        if missing < k:
            low = mid + 1
        else:
            high = mid - 1
    return low + k
```
