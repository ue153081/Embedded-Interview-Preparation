# BS-10 — Square Root of a Number

**Playlist:** [takeUforward BS-10](https://www.youtube.com/playlist?list=PLgUwDviBIf0pMFMWuuvDNMAkoQFi-h0ZF)

## Problem

You are given a non-negative integer `n`. Return the **integer square root** of `n`, i.e. the greatest integer `x` such that `x * x <= n`. Do not use a built-in square-root function.

**Examples**

- `n = 4` → `2`
- `n = 8` → `2` (since `2^2 = 4` and `3^2 = 9 > 8`)
- `n = 0` → `0`

**Constraints:** `0 <= n <= 2^31 - 1`.

## Approaches

**1. Brute force**  
Try `x = 1, 2, 3, ...` until `x * x` exceeds `n`.  
Time: O(√n) · Space: O(1)

**2. Optimized — binary search on the answer**  
Search `x` in `[1, n/2]`. If `mid * mid <= n`, `mid` is feasible and you try larger; otherwise search smaller.  
Time: O(log n) · Space: O(1)

## Pseudocode (optimized)

```
floor_sqrt(n):
    if n < 2: return n
    low ← 1, high ← n / 2, ans ← 1
    while low ≤ high:
        mid ← low + (high - low) / 2
        if mid * mid ≤ n:
            ans ← mid
            low ← mid + 1
        else:
            high ← mid - 1
    return ans
```

## Solution (optimized)

```python
def floor_sqrt(n: int) -> int:
    if n < 2:
        return n
    low, high, ans = 1, n // 2, 1
    while low <= high:
        mid = low + (high - low) // 2
        if mid * mid <= n:
            ans = mid
            low = mid + 1
        else:
            high = mid - 1
    return ans
```
