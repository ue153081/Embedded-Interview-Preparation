"""BS-1 — Binary search on a sorted array (iterative + recursive)."""

from typing import List


def binary_search_iterative(nums: List[int], x: int) -> int:
    """Return any index i with nums[i] == x, else -1. nums must be sorted."""
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == x:
            return mid
        if nums[mid] < x:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def binary_search_recursive(nums: List[int], x: int) -> int:
    def rec(low: int, high: int) -> int:
        if low > high:
            return -1
        mid = low + (high - low) // 2
        if nums[mid] == x:
            return mid
        if nums[mid] < x:
            return rec(mid + 1, high)
        return rec(low, mid - 1)

    return rec(0, len(nums) - 1)


def _check(fn):
    assert fn([], 1) == -1
    assert fn([7], 7) == 0
    assert fn([7], 3) == -1
    assert fn([1, 3, 5, 7, 9], 7) == 3
    assert fn([1, 3, 5, 7, 9], 1) == 0
    assert fn([1, 3, 5, 7, 9], 9) == 4
    assert fn([1, 3, 5, 7, 9], 6) == -1
    assert fn([1, 3, 5, 7, 9], 0) == -1
    assert fn([1, 3, 5, 7, 9], 10) == -1
    idx = fn([2, 2, 2, 2], 2)
    assert idx != -1 and 0 <= idx < 4
    assert fn([2, 2, 2, 2], 3) == -1
    print(fn.__name__, "ok")


if __name__ == "__main__":
    _check(binary_search_iterative)
    _check(binary_search_recursive)
    print("all passed")
