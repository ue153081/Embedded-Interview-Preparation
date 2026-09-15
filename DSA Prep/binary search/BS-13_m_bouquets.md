# BS-13 — Minimum Days to Make M Bouquets

**Playlist:** [takeUforward BS-13](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You have `n` flowers in a row. `bloomDay[i]` is the day the `i`th flower blooms. Once bloomed, a flower stays bloomed.

To make one bouquet you need `k` **adjacent** bloomed flowers. You want `m` bouquets. Flowers cannot be reused across bouquets.

Return the **minimum day** on which you can make `m` bouquets. If it is impossible, return `-1`.

**Examples**

- `bloomDay = [1, 10, 3, 10, 2]`, `m = 3`, `k = 1` → `3`
- `bloomDay = [1, 10, 3, 10, 2]`, `m = 3`, `k = 2` → `-1` (need 6 flowers, only 5 exist)
- `bloomDay = [7, 7, 7, 7, 12, 7, 7]`, `m = 2`, `k = 3` → `12`

**Constraints:** `1 <= n <= 10^5`, `1 <= m, k <= 10^6`. If `m * k > n`, answer is `-1`.

## Approaches

**1. Brute force**  
Try every day from `min(bloomDay)` to `max(bloomDay)` and count how many adjacent groups of `k` bloomed flowers you can cut.  
Time: O((max - min) · n) · Space: O(1)

**2. Optimized — binary search on the day**  
If you can make `m` bouquets by day `d`, you can also make them by any later day. Search days in `[min, max]`.  
Time: O(n log (max_day)) · Space: O(1)

## Pseudocode (optimized)

```
min_days(bloom, m, k):
    if m * k > n: return -1
    low ← min(bloom), high ← max(bloom), ans ← -1

    can_make(day):
        bouquets ← 0, adjacent ← 0
        for d in bloom:
            if d ≤ day:
                adjacent ← adjacent + 1
                if adjacent = k:
                    bouquets ← bouquets + 1
                    adjacent ← 0
            else:
                adjacent ← 0
        return bouquets ≥ m

    while low ≤ high:
        mid ← low + (high - low) / 2
        if can_make(mid):
            ans ← mid
            high ← mid - 1
        else:
            low ← mid + 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def min_days_bouquets(bloom: List[int], m: int, k: int) -> int:
    n = len(bloom)
    if m * k > n:
        return -1
    low, high = min(bloom), max(bloom)
    ans = -1

    def can_make(day: int) -> bool:
        bouquets = adjacent = 0
        for d in bloom:
            if d <= day:
                adjacent += 1
                if adjacent == k:
                    bouquets += 1
                    adjacent = 0
            else:
                adjacent = 0
        return bouquets >= m

    while low <= high:
        mid = low + (high - low) // 2
        if can_make(mid):
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans
```
