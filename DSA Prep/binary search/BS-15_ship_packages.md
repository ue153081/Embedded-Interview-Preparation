# BS-15 — Capacity to Ship Packages Within D Days

**Playlist:** [takeUforward BS-15](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

A conveyor belt has `n` packages in order; `weights[i]` is the weight of the `i`th package. You must ship them **in this order** (you may not reorder).

Each day you load a contiguous prefix of the remaining packages onto the ship without exceeding capacity `c`. You have exactly `days` days.

Return the **least capacity** `c` that still lets you ship everything in at most `days` days.

**Examples**

- `weights = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`, `days = 5` → `15`
- `weights = [3, 2, 2, 4, 1, 4]`, `days = 3` → `6`

**Constraints:** `1 <= n <= 5 * 10^4`, `1 <= days <= n`. Capacity is at least `max(weights)` (a package cannot be split).

## Approaches

**1. Brute force**  
Try every capacity from `max(weights)` to `sum(weights)`.  
Time: O((sum - max) · n) · Space: O(1)

**2. Optimized — binary search on capacity**  
A larger capacity never needs more days. Greedily count days used for a candidate capacity.  
Time: O(n log sum(weights)) · Space: O(1)

## Pseudocode (optimized)

```
ship_within_days(weights, days):
    low ← max(weights), high ← sum(weights), ans ← high

    can_ship(cap):
        used ← 1, load ← 0
        for w in weights:
            if load + w > cap:
                used ← used + 1
                load ← 0
            load ← load + w
        return used ≤ days

    while low ≤ high:
        mid ← low + (high - low) / 2
        if can_ship(mid):
            ans ← mid
            high ← mid - 1
        else:
            low ← mid + 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def ship_within_days(weights: List[int], days: int) -> int:
    low, high = max(weights), sum(weights)
    ans = high

    def can_ship(cap: int) -> bool:
        used, load = 1, 0
        for w in weights:
            if load + w > cap:
                used += 1
                load = 0
            load += w
        return used <= days

    while low <= high:
        mid = low + (high - low) // 2
        if can_ship(mid):
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans
```
