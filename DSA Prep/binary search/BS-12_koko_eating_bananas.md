# BS-12 — Koko Eating Bananas

**Playlist:** [takeUforward BS-12](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

Koko has `n` piles of bananas, `piles[i]` bananas in the `i`th pile. Guards return in `h` hours.

Each hour she chooses **one** pile and eats `k` bananas from it (or the whole pile if fewer than `k` remain). She never starts a second pile in the same hour.

Return the **minimum integer eating speed** `k` such that she can finish all piles in at most `h` hours.

**Examples**

- `piles = [3, 6, 7, 11]`, `h = 8` → `4`
- `piles = [30, 11, 23, 4, 20]`, `h = 5` → `30`
- `piles = [30, 11, 23, 4, 20]`, `h = 6` → `23`

**Constraints:** `1 <= n <= 10^4`, `n <= h <= 10^9`, `1 <= piles[i] <= 10^9`.

## Approaches

**1. Brute force**  
Try every speed `k` from `1` to `max(piles)` and take the smallest that finishes in `<= h` hours. Hours for a speed is `sum(ceil(pile / k))`.  
Time: O(max(piles) · n) · Space: O(1)

**2. Optimized — binary search on speed**  
Hours needed **decreases** as `k` grows, so the feasibility predicate is monotonic. Search `k` in `[1, max(piles)]`.  
Time: O(n log max(piles)) · Space: O(1)

## Pseudocode (optimized)

```
min_eating_speed(piles, h):
    low ← 1, high ← max(piles), ans ← high
    while low ≤ high:
        mid ← low + (high - low) / 2
        hours ← sum over piles of ceil(pile / mid)
        if hours ≤ h:
            ans ← mid
            high ← mid - 1
        else:
            low ← mid + 1
    return ans
```

## Solution (optimized)

```python
from typing import List


def min_eating_speed(piles: List[int], h: int) -> int:
    low, high = 1, max(piles)
    ans = high
    while low <= high:
        mid = low + (high - low) // 2
        hours = sum((p + mid - 1) // mid for p in piles)
        if hours <= h:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans
```
