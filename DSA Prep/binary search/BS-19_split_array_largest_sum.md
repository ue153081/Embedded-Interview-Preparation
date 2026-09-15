# BS-19 — Split Array Largest Sum (Painter’s Partition)

**Playlist:** [takeUforward BS-19](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

Given an integer array `nums` and an integer `k`, split `nums` into `k` **non-empty contiguous** subarrays.

The **largest sum** among those subarrays should be as small as possible. Return that minimized largest sum.

This is the same numeric problem as book allocation (BS-18) and painter’s partition (each painter paints a contiguous segment, minimize the time = max segment sum).

**Examples**

- `nums = [7, 2, 5, 10, 8]`, `k = 2` → `18`  
  Split `[7, 2, 5]` and `[10, 8]`
- `nums = [1, 2, 3, 4, 5]`, `k = 2` → `9` (`[1, 2, 3]` and `[4, 5]`)

**Constraints:** `1 <= k <= n <= 10^4` (or larger in some judges).

## Approaches

**1. Brute force**  
Enumerate all placements of `k - 1` cuts.  
Time: exponential

**2. Optimized — binary search on the largest subarray sum**  
Identical to BS-18: search the limit `L` in `[max(nums), sum(nums)]` and count how many subarrays you need if none may exceed `L`.  
Time: O(n log sum) · Space: O(1)

## Pseudocode (optimized)

```
split_array(nums, k):
    low ← max(nums), high ← sum(nums), ans ← high

    splits_needed(limit):
        parts ← 1, acc ← 0
        for x in nums:
            if acc + x > limit:
                parts ← parts + 1
                acc ← 0
            acc ← acc + x
        return parts

    while low ≤ high:
        mid ← low + (high - low) / 2
        if splits_needed(mid) ≤ k:
            ans ← mid
            high ← mid - 1
        else:
            low ← mid + 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def split_array_largest_sum(nums: List[int], k: int) -> int:
    low, high = max(nums), sum(nums)
    ans = high

    def splits_needed(limit: int) -> int:
        parts, acc = 1, 0
        for x in nums:
            if acc + x > limit:
                parts += 1
                acc = 0
            acc += x
        return parts

    while low <= high:
        mid = low + (high - low) // 2
        if splits_needed(mid) <= k:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans
```
