# BS-20 — Minimise Maximum Distance Between Gas Stations

**Playlist:** [takeUforward BS-20](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given `n` gas stations already placed on a number line at strictly increasing positions `stations[0] < stations[1] < ... < stations[n - 1]`.

You may add **exactly `k` extra stations** anywhere on the line (including between existing ones). You cannot move the original stations.

After adding them, consider every pair of **adjacent** stations (original or new). Return the **minimum possible value of the maximum adjacent distance**. The answer is a floating-point number; a small absolute error (e.g. `1e-6`) is acceptable.

**Examples**

- `stations = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`, `k = 9` → `0.5`
- `stations = [1, 13, 17, 23]`, `k = 5` → about `3.0` depending on placement

**Constraints:** `2 <= n <= 10^5`, `0 <= k <= 10^6`.

## Approaches

**1. Brute / better — greedy with a max-heap**  
Always split the current largest gap (track how many stations already sit in that original gap).  
Time: O(k log n) · Space: O(n)  
Too slow when `k` is huge.

**2. Optimized — binary search on the real-valued distance**  
For a candidate max distance `d`, each original gap of length `g` needs `ceil(g / d) - 1` extra stations. If the total needed is `<= k`, `d` is feasible. Search `d` in `[0, max_gap]` with enough iterations for precision.  
Time: O(n · iterations) · Space: O(1)

## Pseudocode (optimized)

```
minmax_gas_distance(stations, k):
    low ← 0, high ← stations[n - 1] - stations[0]

    needed(d):
        extra ← 0
        for each adjacent gap g:
            extra ← extra + ceil(g / d) - 1
        return extra

    repeat ~80 times:
        mid ← (low + high) / 2
        if needed(mid) ≤ k:
            high ← mid
        else:
            low ← mid
    return high
```

## Solution (optimized)

```python
from math import ceil
from typing import List


def minmax_gas_station_distance(stations: List[int], k: int) -> float:
    stations = sorted(stations)
    low, high = 0.0, float(stations[-1] - stations[0])

    def needed(dist: float) -> int:
        extra = 0
        for i in range(1, len(stations)):
            gap = stations[i] - stations[i - 1]
            extra += ceil(gap / dist) - 1
        return extra

    for _ in range(80):
        mid = (low + high) / 2
        if needed(mid) <= k:
            high = mid
        else:
            low = mid
    return high
```
