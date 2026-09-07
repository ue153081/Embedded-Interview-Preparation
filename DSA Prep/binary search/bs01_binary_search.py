"""BS-1 — Binary search on a sorted array (optimized)."""

from typing import List


def binary_search(nums: List[int], x: int) -> int:
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


if __name__ == "__main__":
    assert binary_search([], 1) == -1
    assert binary_search([7], 7) == 0
    assert binary_search([1, 3, 5, 7, 9], 7) == 3
    assert binary_search([1, 3, 5, 7, 9], 6) == -1
    print("ok")
