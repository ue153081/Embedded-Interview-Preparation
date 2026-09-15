# BS-17 — Aggressive Cows

**Playlist:** [takeUforward BS-17](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

There are `n` stalls at distinct positions given in array `stalls`. You must place `cows` aggressive cows into these stalls (at most one cow per stall) so that the **minimum distance between any two cows is as large as possible**.

Return that maximum possible minimum distance.

**Examples**

- `stalls = [1, 2, 8, 4, 9]`, `cows = 3` → `3`  
  One optimal placement: positions `1, 4, 9` or `1, 4, 8`.
- `stalls = [1, 2, 4, 8, 9]`, `cows = 4` → `1`

**Constraints:** `2 <= cows <= n <= 10^5`. Sort stalls first if they are unsorted.

## Approaches

**1. Brute force**  
After sorting, try every distance from `1` to `stalls[-1] - stalls[0]`. For each distance, greedily place cows left to right.  
Time: O((maxDist) · n) · Space: O(1) besides sort

**2. Optimized — binary search on the minimum distance**  
If distance `d` is placeable, every smaller distance is too. Search `d` in `[1, max_pos - min_pos]` and greedily check.  
Time: O(n log (max - min)) after O(n log n) sort · Space: O(1) extra if you sort in place

## Pseudocode (optimized)

```
aggressive_cows(stalls, cows):
    sort stalls
    low ← 1, high ← stalls[n - 1] - stalls[0], ans ← 0

    can_place(dist):
        placed ← 1, last ← stalls[0]
        for x in stalls[1..]:
            if x - last ≥ dist:
                placed ← placed + 1
                last ← x
                if placed ≥ cows: return true
        return false

    while low ≤ high:
        mid ← low + (high - low) / 2
        if can_place(mid):
            ans ← mid
            low ← mid + 1
        else:
            high ← mid - 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def aggressive_cows(stalls: List[int], cows: int) -> int:
    stalls = sorted(stalls)
    low, high = 1, stalls[-1] - stalls[0]
    ans = 0

    def can_place(dist: int) -> bool:
        placed, last = 1, stalls[0]
        for x in stalls[1:]:
            if x - last >= dist:
                placed += 1
                last = x
                if placed >= cows:
                    return True
        return False

    while low <= high:
        mid = low + (high - low) // 2
        if can_place(mid):
            ans = mid
            low = mid + 1
        else:
            high = mid - 1
    return ans
```
