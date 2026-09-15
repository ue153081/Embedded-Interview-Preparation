# BS-6 — Minimum in Rotated Sorted Array

**Playlist:** [takeUforward BS-6](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an array `nums` of **unique** integers that was originally sorted in ascending order and then rotated between `1` and `n` times.

Return the **minimum** element. You must use O(log n) time.

**Examples**

- `nums = [3, 4, 5, 1, 2]` → `1`
- `nums = [4, 5, 6, 7, 0, 1, 2]` → `0`
- `nums = [11, 13, 15, 17]` → `11` (rotated `n` times, still sorted)

**Constraints:** `1 <= n <= 10^5`, all unique.

## Approaches

**1. Brute force**  
Scan for the minimum.  
Time: O(n) · Space: O(1)

**2. Optimized — binary search toward the unsorted half**  
If `nums[low] <= nums[high]`, the current window is already sorted, so `nums[low]` is the min of this window. Otherwise the left half is sorted iff `nums[low] <= nums[mid]`; then the pivot (minimum) is strictly to the right. Else the pivot is at `mid` or to the left. Track the minimum seen.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
find_min_rotated(nums):
    low ← 0, high ← n - 1
    ans ← nums[0]
    while low ≤ high:
        if nums[low] ≤ nums[high]:
            ans ← min(ans, nums[low])
            break
        mid ← low + (high - low) / 2
        ans ← min(ans, nums[mid])
        if nums[low] ≤ nums[mid]:
            low ← mid + 1
        else:
            high ← mid - 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def find_min_rotated(nums: List[int]) -> int:
    low, high = 0, len(nums) - 1
    ans = nums[0]
    while low <= high:
        if nums[low] <= nums[high]:
            ans = min(ans, nums[low])
            break
        mid = low + (high - low) // 2
        ans = min(ans, nums[mid])
        if nums[low] <= nums[mid]:
            low = mid + 1
        else:
            high = mid - 1
    return ans
```
