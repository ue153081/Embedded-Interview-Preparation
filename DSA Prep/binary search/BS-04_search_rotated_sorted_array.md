# BS-4 — Search in Rotated Sorted Array I

**Playlist:** [takeUforward BS-4](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

A strictly increasing array of **distinct** integers was rotated some unknown number of times (possibly zero). For example `[0, 1, 2, 4, 5, 6, 7]` might become `[4, 5, 6, 7, 0, 1, 2]`.

You are given this rotated array `nums` and an integer `target`. Return the index of `target`, or `-1` if it is not present.

You must solve it in O(log n) time.

**Examples**

- `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 0` → `4`
- `nums = [4, 5, 6, 7, 0, 1, 2]`, `target = 3` → `-1`
- `nums = [1]`, `target = 1` → `0`

**Constraints:** `1 <= n <= 10^5`, all values unique.

## Approaches

**1. Brute force**  
Linear scan.  
Time: O(n) · Space: O(1)

**2. Optimized — identify the sorted half**  
In a rotated unique array, at least one of `[low, mid]` and `[mid, high]` is strictly sorted. If `nums[low] <= nums[mid]`, the left half is sorted: if `target` lies in `[nums[low], nums[mid])`, search left, otherwise right. Symmetric logic for a sorted right half.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
search_rotated(nums, target):
    low ← 0, high ← n - 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        if nums[mid] = target:
            return mid
        if nums[low] ≤ nums[mid]:          # left half sorted
            if nums[low] ≤ target < nums[mid]:
                high ← mid - 1
            else:
                low ← mid + 1
        else:                              # right half sorted
            if nums[mid] < target ≤ nums[high]:
                low ← mid + 1
            else:
                high ← mid - 1
    return -1
```

## Solution (optimized)

```python
from typing import List


def search_rotated(nums: List[int], target: int) -> int:
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return mid
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1
```
