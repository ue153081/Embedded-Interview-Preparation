# BS-14 — Find the Smallest Divisor Given a Threshold

**Playlist:** [takeUforward BS-14](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given an integer array `nums` and an integer `threshold`.

Choose a positive integer divisor `d`. Replace every `nums[i]` with `ceil(nums[i] / d)`, then sum those values.

Return the **smallest** `d` such that this sum is `<= threshold`.

**Examples**

- `nums = [1, 2, 5, 9]`, `threshold = 6` → `5`  
  (`ceil` sums: d=5 → 1+1+1+2 = 5)
- `nums = [44, 22, 33, 11, 1]`, `threshold = 5` → `44`

**Constraints:** `1 <= n <= 5 * 10^4`, `1 <= nums[i] <= 10^6`, `n <= threshold <= 10^6`.

## Approaches

**1. Brute force**  
Try `d = 1, 2, ..., max(nums)`.  
Time: O(max(nums) · n) · Space: O(1)

**2. Optimized — binary search on the divisor**  
Larger `d` only **decreases** the sum, so feasibility is monotonic. Search `d` in `[1, max(nums)]`.  
Time: O(n log max(nums)) · Space: O(1)

## Pseudocode (optimized)

```
smallest_divisor(nums, threshold):
    low ← 1, high ← max(nums), ans ← high
    while low ≤ high:
        mid ← low + (high - low) / 2
        total ← sum of ceil(x / mid) for x in nums
        if total ≤ threshold:
            ans ← mid
            high ← mid - 1
        else:
            low ← mid + 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def smallest_divisor(nums: List[int], threshold: int) -> int:
    low, high = 1, max(nums)
    ans = high
    while low <= high:
        mid = low + (high - low) // 2
        total = sum((x + mid - 1) // mid for x in nums)
        if total <= threshold:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans
```
