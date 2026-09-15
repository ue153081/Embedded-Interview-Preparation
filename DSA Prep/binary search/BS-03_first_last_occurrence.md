# BS-3 — First and Last Occurrence / Count Occurrences

**Playlist:** [takeUforward BS-3](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given a sorted non-decreasing integer array `nums` of length `n` (duplicates allowed) and an integer `target`.

1. Return the **first** and **last** indices at which `target` appears, as a pair `(first, last)`. If `target` is not present, return `(-1, -1)`.
2. Using those indices, return how many times `target` occurs in `nums`.

**Examples**

- `nums = [2, 4, 6, 8, 8, 8, 11]`, `target = 8` → first/last `(3, 5)`, count `3`
- `nums = [2, 4, 6, 8, 8, 8, 11]`, `target = 5` → `(-1, -1)`, count `0`

**Constraints:** `0 <= n <= 10^5`. Expected time is logarithmic.

## Approaches

**1. Brute force**  
One left-to-right pass: record the first and last index equal to `target`. Count is `last - first + 1`.  
Time: O(n) · Space: O(1)

**2. Optimized — two bound searches**  
First occurrence is the lower bound of `target` (first index with `nums[i] >= target`), provided that value equals `target`. Last occurrence is upper bound minus one. Count is `last - first + 1`.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
first_last(nums, target):
    first ← lower_bound(nums, target)
    if first = n or nums[first] ≠ target:
        return (-1, -1)
    last ← upper_bound(nums, target) - 1
    return (first, last)

count(nums, target):
    (first, last) ← first_last(nums, target)
    if first = -1: return 0
    return last - first + 1
```

## Solution (optimized)

```python
from typing import List, Tuple


def lower_bound(nums: List[int], x: int) -> int:
    low, high, ans = 0, len(nums) - 1, len(nums)
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] >= x:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans


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


def first_last_occurrence(nums: List[int], target: int) -> Tuple[int, int]:
    first = lower_bound(nums, target)
    if first == len(nums) or nums[first] != target:
        return -1, -1
    last = upper_bound(nums, target) - 1
    return first, last


def count_occurrences(nums: List[int], target: int) -> int:
    first, last = first_last_occurrence(nums, target)
    if first == -1:
        return 0
    return last - first + 1
```
