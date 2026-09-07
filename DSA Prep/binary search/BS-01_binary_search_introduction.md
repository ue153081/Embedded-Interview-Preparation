# BS-1 — Binary Search

**Playlist:** [takeUforward BS-1](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

Given a **sorted** array `nums` (non-decreasing) and a target `x`, return any index `i` such that `nums[i] == x`. If `x` is not present, return `-1`.

## Approaches

**1. Brute force — linear scan**  
Walk from left to right and compare each element with `x`.  
Time: O(n) · Space: O(1)  
Correct, but ignores that the array is already sorted.

**2. Optimized — binary search**  
Keep an inclusive window `[low, high]`. Compare `x` with the middle element and throw away half the window each step:

- `nums[mid] == x` → found
- `nums[mid] < x` → search right (`low = mid + 1`)
- `nums[mid] > x` → search left (`high = mid - 1`)

Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
binary_search(nums, x):
    low ← 0
    high ← n - 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        if nums[mid] = x:
            return mid
        else if nums[mid] < x:
            low ← mid + 1
        else:
            high ← mid - 1
    return -1
```

## Solution (optimized)

```python
from typing import List


def binary_search(nums: List[int], x: int) -> int:
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == x:
            return mid
        if nums[mid] < x:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```
