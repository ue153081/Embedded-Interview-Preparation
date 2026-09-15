# BS-11 — Nth Root of an Integer

**Playlist:** [takeUforward BS-11](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given two positive integers `n` and `m`. Find the integer `x` such that `x^n = m`. If no such integer exists ( `m` is not a perfect `n`th power), return `-1`.

**Examples**

- `n = 3`, `m = 27` → `3`
- `n = 4`, `m = 69` → `-1`
- `n = 2`, `m = 16` → `4`

**Constraints:** `1 <= n <= 30`, `0 <= m <= 10^9` (treat `m = 0` or `1` as returning `m`).

## Approaches

**1. Brute force**  
Try `x = 1, 2, ...` until `x^n` reaches or passes `m`.  
Time: O(m^(1/n) · n) · Space: O(1)

**2. Optimized — binary search on x**  
Search `x` in `[1, m]`. Compare `mid^n` with `m` (Python big integers make overflow a non-issue). Equal → answer; smaller → go right; larger → go left. If the loop ends without equality, return `-1`.  
Time: O(log m) power-checks · Space: O(1)

## Pseudocode (optimized)

```
nth_root(n, m):
    if m = 0 or m = 1: return m
    low ← 1, high ← m
    while low ≤ high:
        mid ← low + (high - low) / 2
        val ← mid ^ n
        if val = m: return mid
        if val < m: low ← mid + 1
        else: high ← mid - 1
    return -1
```

## Solution (optimized)

```python
def nth_root(n: int, m: int) -> int:
    if m == 0 or m == 1:
        return m
    low, high = 1, m
    while low <= high:
        mid = low + (high - low) // 2
        val = mid**n
        if val == m:
            return mid
        if val < m:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```
