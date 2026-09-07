# BS-7 — How Many Times the Array Has Been Rotated

**Playlist:** [takeUforward BS-7](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an array `nums` of unique integers that was originally sorted in ascending order and then rotated `r` times to the left (or equivalently, the minimum was moved from index `0` to index `r`).

Return `r` — the number of rotations. This is exactly the **index of the minimum** element. If the array is still fully sorted, return `0`.

**Examples**

- `nums = [4, 5, 6, 7, 0, 1, 2]` → `4`
- `nums = [1, 2, 3, 4]` → `0`
- `nums = [2, 3, 4, 1]` → `3`

**Constraints:** `1 <= n <= 10^5`, unique values.

## Approaches

**1. Brute force**  
Find the index of the minimum with a linear scan.  
Time: O(n) · Space: O(1)

**2. Optimized — same search as finding the minimum**  
Run the BS-6 search but keep the **index** of the smallest value instead of only the value. That index is the rotation count.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
rotation_count(nums):
    low ← 0, high ← n - 1
    index ← 0
    while low ≤ high:
        if nums[low] ≤ nums[high]:
            if nums[low] < nums[index]:
                index ← low
            break
        mid ← low + (high - low) / 2
        if nums[mid] < nums[index]:
            index ← mid
        if nums[low] ≤ nums[mid]:
            low ← mid + 1
        else:
            high ← mid - 1
    return index
```

## Solution (optimized)

```python
from typing import List


def rotation_count(nums: List[int]) -> int:
    low, high = 0, len(nums) - 1
    index = 0
    while low <= high:
        if nums[low] <= nums[high]:
            if nums[low] < nums[index]:
                index = low
            break
        mid = low + (high - low) // 2
        if nums[mid] < nums[index]:
            index = mid
        if nums[low] <= nums[mid]:
            low = mid + 1
        else:
            high = mid - 1
    return index
```
