# BS-5 — Search in Rotated Sorted Array II

**Playlist:** [takeUforward BS-5](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

Same setup as BS-4, except `nums` **may contain duplicates**. The array was originally sorted non-decreasing and then rotated.

Given `nums` and `target`, return `true` if `target` exists, otherwise `false`.

**Examples**

- `nums = [2, 5, 6, 0, 0, 1, 2]`, `target = 0` → `true`
- `nums = [2, 5, 6, 0, 0, 1, 2]`, `target = 3` → `false`
- `nums = [1, 1, 1, 1, 1, 1, 1]`, `target = 2` → `false`

**Constraints:** `1 <= n <= 10^5`. Worst-case time may degrade because of duplicates; still use the rotated binary-search template.

## Approaches

**1. Brute force**  
Linear scan.  
Time: O(n) · Space: O(1)

**2. Optimized — rotated search with duplicate shrink**  
Same “sorted half” test as BS-4, but `nums[low] == nums[mid] == nums[high]` makes it impossible to tell which half is sorted. In that case skip the two ends (`low += 1`, `high -= 1`) and continue. Average O(log n); worst case O(n) when almost all values are equal.  
Space: O(1)

## Pseudocode (optimized)

```
search_rotated_duplicates(nums, target):
    low ← 0, high ← n - 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        if nums[mid] = target:
            return true
        if nums[low] = nums[mid] = nums[high]:
            low ← low + 1
            high ← high - 1
            continue
        if nums[low] ≤ nums[mid]:
            if nums[low] ≤ target < nums[mid]:
                high ← mid - 1
            else:
                low ← mid + 1
        else:
            if nums[mid] < target ≤ nums[high]:
                low ← mid + 1
            else:
                high ← mid - 1
    return false
```

## Solution (optimized)

```python
from typing import List


def search_rotated_duplicates(nums: List[int], target: int) -> bool:
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return True
        if nums[low] == nums[mid] == nums[high]:
            low += 1
            high -= 1
            continue
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
    return False
```
