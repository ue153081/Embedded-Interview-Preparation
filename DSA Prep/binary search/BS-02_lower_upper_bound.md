# BS-2 — Lower Bound, Upper Bound, Search Insert Position, Floor and Ceil

**Playlist:** [takeUforward BS-2](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

These four questions share the same binary-search-on-a-boundary idea. You are always given a **sorted non-decreasing** integer array `nums` of length `n`.

---

## Problem A — Lower bound

Return the smallest index `i` such that `nums[i] >= x`. If every element is smaller than `x`, return `n` (the insert-at-end index).

**Example:** `nums = [1, 2, 2, 3]`, `x = 2` → `1`

## Problem B — Upper bound

Return the smallest index `i` such that `nums[i] > x`. If none, return `n`.

**Example:** `nums = [1, 2, 2, 3]`, `x = 2` → `3`

## Problem C — Search insert position

Given a **distinct** sorted array and `target`, return the index if `target` is found. If not, return the index where it **would be inserted** to keep the array sorted. This is the same answer as lower bound.

**Example:** `nums = [1, 3, 5, 6]`, `target = 2` → `1`

## Problem D — Floor and ceil

- **Floor** of `x` is the largest value in `nums` that is `<= x` (or `-1` if none).
- **Ceil** of `x` is the smallest value in `nums` that is `>= x` (or `-1` if none).

Return `(floor, ceil)`.

**Example:** `nums = [1, 2, 8, 10]`, `x = 5` → `(2, 8)`

## Approaches

**1. Brute force**  
Scan left to right and stop at the first index that satisfies the predicate (`>= x` or `> x`). Floor/ceil are the last `<= x` and first `>= x`.  
Time: O(n) · Space: O(1)

**2. Optimized — binary search on the first true index**  
Keep the best feasible index `ans` while shrinking the window. For lower bound, whenever `nums[mid] >= x`, record `mid` and search left; otherwise search right. Upper bound uses `nums[mid] > x`. Floor is `nums[lower_bound - 1]` (if that index exists); ceil is `nums[lower_bound]` (if in range).  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized) — lower bound

```
lower_bound(nums, x):
    low ← 0, high ← n - 1, ans ← n
    while low ≤ high:
        mid ← low + (high - low) / 2
        if nums[mid] ≥ x:
            ans ← mid
            high ← mid - 1
        else:
            low ← mid + 1
    return ans
```

Upper bound is the same with `nums[mid] > x`. Search insert returns `lower_bound`. Floor/ceil are derived from that index.

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


def search_insert(nums: List[int], target: int) -> int:
    return lower_bound(nums, target)


def floor_ceil(nums: List[int], x: int) -> Tuple[int, int]:
    n = len(nums)
    lb = lower_bound(nums, x)
    ceil_v = nums[lb] if lb < n else -1
    if lb < n and nums[lb] == x:
        floor_v = x
    else:
        floor_v = nums[lb - 1] if lb > 0 else -1
    return floor_v, ceil_v
```
