# BS-1 — Binary Search

**Playlist:** [takeUforward BS-1](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an integer array `nums` of length `n` that is sorted in **non-decreasing** order, and an integer `target`.

Implement a function that searches for `target` in `nums` and returns its **index**. If `target` does not appear in `nums`, return `-1`.

If `target` occurs more than once, returning **any** matching index is acceptable. You should aim for better than linear time.

**Examples**

- `nums = [1, 3, 5, 7, 9]`, `target = 7` → `3`
- `nums = [1, 3, 5, 7, 9]`, `target = 6` → `-1`
- `nums = []`, `target = 1` → `-1`

**Constraints:** `0 <= n <= 10^5`, array is sorted non-decreasing.

## Approaches

**1. Brute force — linear scan**  
Compare every element with `target`.  
Time: O(n) · Space: O(1)

**2. Optimized — binary search**  
Because the array is sorted, compare `target` with the middle of the remaining window `[low, high]` and discard half the elements each step.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
binary_search(nums, target):
    low ← 0
    high ← n - 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        if nums[mid] = target:
            return mid
        else if nums[mid] < target:
            low ← mid + 1
        else:
            high ← mid - 1
    return -1
```

## Solution (optimized)

```python
from typing import List


def binary_search(nums: List[int], target: int) -> int:
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```
