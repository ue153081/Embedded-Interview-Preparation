# BS-8 — Single Element in a Sorted Array

**Playlist:** [takeUforward BS-8](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given a sorted array `nums` in which every element appears **exactly twice**, except for one element that appears **exactly once**. Return that single element.

You must run in O(log n) time and O(1) extra space.

**Examples**

- `nums = [1, 1, 2, 3, 3, 4, 4, 8, 8]` → `2`
- `nums = [3, 3, 7, 7, 10, 11, 11]` → `10`

**Constraints:** `1 <= n <= 10^5`, `n` is odd. Pairs sit next to each other.

## Approaches

**1. Brute force**  
XOR all elements (or scan checking neighbors).  
Time: O(n) · Space: O(1)

**2. Optimized — binary search on pair alignment**  
Before the single element, pairs sit at indices `(even, odd)`. After it, pairs sit at `(odd, even)`. Force `mid` onto an even index. If `nums[mid] == nums[mid + 1]`, the single element is to the right; otherwise it is at `mid` or to the left.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
single_non_duplicate(nums):
    low ← 0, high ← n - 1
    while low < high:
        mid ← low + (high - low) / 2
        if mid is odd:
            mid ← mid - 1
        if nums[mid] = nums[mid + 1]:
            low ← mid + 2
        else:
            high ← mid
    return nums[low]
```

## Solution (optimized)

```python
from typing import List


def single_non_duplicate(nums: List[int]) -> int:
    low, high = 0, len(nums) - 1
    while low < high:
        mid = low + (high - low) // 2
        if mid % 2 == 1:
            mid -= 1
        if nums[mid] == nums[mid + 1]:
            low = mid + 2
        else:
            high = mid
    return nums[low]
```
