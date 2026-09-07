# BS-9 — Find Peak Element

**Playlist:** [takeUforward BS-9](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

A **peak** is an element that is strictly greater than its neighbors. For endpoints, only the single inner neighbor is considered. `nums[-1]` and `nums[n]` may be treated as `-∞`, so a strictly increasing or decreasing array still has a peak at an end.

Given an integer array `nums`, return the **index** of any peak. If several peaks exist, any one is accepted. You must use O(log n) time.

**Examples**

- `nums = [1, 2, 3, 1]` → `2` (value `3`)
- `nums = [1, 2, 1, 3, 5, 6, 4]` → `1` or `5`

**Constraints:** `1 <= n <= 10^5`. Adjacent elements are not equal.

## Approaches

**1. Brute force**  
Scan each index and test neighbors.  
Time: O(n) · Space: O(1)

**2. Optimized — climb the slope**  
If `nums[mid] < nums[mid + 1]`, a peak exists on the right (the sequence is still rising). Otherwise a peak exists at `mid` or on the left. Handle `n == 1` and the two ends first.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
find_peak_element(nums):
    if n = 1: return 0
    if nums[0] > nums[1]: return 0
    if nums[n - 1] > nums[n - 2]: return n - 1
    low ← 1, high ← n - 2
    while low ≤ high:
        mid ← low + (high - low) / 2
        if nums[mid] > nums[mid - 1] and nums[mid] > nums[mid + 1]:
            return mid
        if nums[mid] < nums[mid + 1]:
            low ← mid + 1
        else:
            high ← mid - 1
```

## Solution (optimized)

```python
from typing import List


def find_peak_element(nums: List[int]) -> int:
    n = len(nums)
    if n == 1:
        return 0
    if nums[0] > nums[1]:
        return 0
    if nums[n - 1] > nums[n - 2]:
        return n - 1
    low, high = 1, n - 2
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] > nums[mid - 1] and nums[mid] > nums[mid + 1]:
            return mid
        if nums[mid] < nums[mid + 1]:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```
