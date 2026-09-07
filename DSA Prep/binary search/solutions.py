"""Optimized Python solutions for takeUforward Binary Search BS-1 to BS-27."""

from __future__ import annotations

from math import ceil
from typing import List, Tuple


# --- BS-1 ---
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


# --- BS-2 ---
def lower_bound(nums: List[int], x: int) -> int:
    """First index i such that nums[i] >= x, or n if none."""
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
    """First index i such that nums[i] > x, or n if none."""
    low, high, ans = 0, len(nums) - 1, len(nums)
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] > x:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans


def search_insert(nums: List[int], x: int) -> int:
    return lower_bound(nums, x)


def floor_ceil(nums: List[int], x: int) -> Tuple[int, int]:
    """Return (floor value, ceil value); -1 if missing."""
    n = len(nums)
    lb = lower_bound(nums, x)
    ceil_v = nums[lb] if lb < n else -1
    if lb < n and nums[lb] == x:
        floor_v = x
    else:
        floor_v = nums[lb - 1] if lb > 0 else -1
    return floor_v, ceil_v


# --- BS-3 ---
def first_last_occurrence(nums: List[int], x: int) -> Tuple[int, int]:
    first = lower_bound(nums, x)
    if first == len(nums) or nums[first] != x:
        return -1, -1
    last = upper_bound(nums, x) - 1
    return first, last


def count_occurrences(nums: List[int], x: int) -> int:
    first, last = first_last_occurrence(nums, x)
    if first == -1:
        return 0
    return last - first + 1


# --- BS-4 ---
def search_rotated(nums: List[int], target: int) -> int:
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return mid
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return -1


# --- BS-5 ---
def search_rotated_duplicates(nums: List[int], target: int) -> bool:
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] == target:
            return True
        if nums[low] == nums[mid] == nums[high]:
            low += 1
            high -= 1
            continue
        if nums[low] <= nums[mid]:
            if nums[low] <= target < nums[mid]:
                high = mid - 1
            else:
                low = mid + 1
        else:
            if nums[mid] < target <= nums[high]:
                low = mid + 1
            else:
                high = mid - 1
    return False


# --- BS-6 ---
def find_min_rotated(nums: List[int]) -> int:
    low, high = 0, len(nums) - 1
    ans = nums[0]
    while low <= high:
        if nums[low] <= nums[high]:
            ans = min(ans, nums[low])
            break
        mid = low + (high - low) // 2
        ans = min(ans, nums[mid])
        if nums[low] <= nums[mid]:
            low = mid + 1
        else:
            high = mid - 1
    return ans


# --- BS-7 ---
def rotation_count(nums: List[int]) -> int:
    low, high = 0, len(nums) - 1
    n = len(nums)
    index = 0
    while low <= high:
        if nums[low] <= nums[high]:
            if nums[low] < nums[index]:
                index = low
            break
        mid = low + (high - low) // 2
        if nums[mid] < nums[index]:
            index = mid
        if nums[low] <= nums[mid]:
            low = mid + 1
        else:
            high = mid - 1
    return index


# --- BS-8 ---
def single_non_duplicate(nums: List[int]) -> int:
    low, high = 0, len(nums) - 1
    while low < high:
        mid = low + (high - low) // 2
        if mid % 2 == 1:
            mid -= 1
        if nums[mid] == nums[mid + 1]:
            low = mid + 2
        else:
            high = mid
    return nums[low]


# --- BS-9 ---
def find_peak_element(nums: List[int]) -> int:
    n = len(nums)
    if n == 1:
        return 0
    if nums[0] > nums[1]:
        return 0
    if nums[n - 1] > nums[n - 2]:
        return n - 1
    low, high = 1, n - 2
    while low <= high:
        mid = low + (high - low) // 2
        if nums[mid] > nums[mid - 1] and nums[mid] > nums[mid + 1]:
            return mid
        if nums[mid] < nums[mid + 1]:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# --- BS-10 ---
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


# --- BS-11 ---
def nth_root(n: int, m: int) -> int:
    """Largest integer x with x^n == m, else -1 if m is not a perfect nth power."""
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


# --- BS-12 ---
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


# --- BS-13 ---
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


# --- BS-14 ---
def smallest_divisor(nums: List[int], threshold: int) -> int:
    low, high = 1, max(nums)
    ans = high
    while low <= high:
        mid = low + (high - low) // 2
        total = sum((x + mid - 1) // mid for x in nums)
        if total <= threshold:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans


# --- BS-15 ---
def ship_within_days(weights: List[int], days: int) -> int:
    low, high = max(weights), sum(weights)
    ans = high

    def can_ship(cap: int) -> bool:
        used = 1
        load = 0
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


# --- BS-16 ---
def find_kth_missing(arr: List[int], k: int) -> int:
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = low + (high - low) // 2
        missing = arr[mid] - (mid + 1)
        if missing < k:
            low = mid + 1
        else:
            high = mid - 1
    return low + k


# --- BS-17 ---
def aggressive_cows(stalls: List[int], cows: int) -> int:
    stalls = sorted(stalls)
    low, high = 1, stalls[-1] - stalls[0]
    ans = 0

    def can_place(dist: int) -> bool:
        placed = 1
        last = stalls[0]
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


# --- BS-18 / BS-19 helper ---
def _min_max_split(nums: List[int], k: int) -> int:
    low, high = max(nums), sum(nums)
    ans = high

    def splits_needed(limit: int) -> int:
        parts = 1
        acc = 0
        for x in nums:
            if acc + x > limit:
                parts += 1
                acc = 0
            acc += x
        return parts

    while low <= high:
        mid = low + (high - low) // 2
        if splits_needed(mid) <= k:
            ans = mid
            high = mid - 1
        else:
            low = mid + 1
    return ans


def allocate_books(pages: List[int], students: int) -> int:
    if students > len(pages):
        return -1
    return _min_max_split(pages, students)


def split_array_largest_sum(nums: List[int], k: int) -> int:
    return _min_max_split(nums, k)


# --- BS-20 ---
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


# --- BS-21 ---
def find_median_sorted_arrays(a: List[int], b: List[int]) -> float:
    if len(a) > len(b):
        a, b = b, a
    n1, n2 = len(a), len(b)
    n = n1 + n2
    left = (n + 1) // 2
    low, high = 0, n1
    while low <= high:
        i = (low + high) // 2
        j = left - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < n1 else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n2 else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if n % 2 == 1:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2.0
        if a_left > b_right:
            high = i - 1
        else:
            low = i + 1
    raise ValueError("invalid input")


# --- BS-22 ---
def kth_element_two_sorted(a: List[int], b: List[int], k: int) -> int:
    """1-indexed k."""
    n1, n2 = len(a), len(b)
    if n1 > n2:
        return kth_element_two_sorted(b, a, k)
    low = max(0, k - n2)
    high = min(k, n1)
    while low <= high:
        i = (low + high) // 2
        j = k - i
        a_left = a[i - 1] if i > 0 else float("-inf")
        a_right = a[i] if i < n1 else float("inf")
        b_left = b[j - 1] if j > 0 else float("-inf")
        b_right = b[j] if j < n2 else float("inf")
        if a_left <= b_right and b_left <= a_right:
            return int(max(a_left, b_left))
        if a_left > b_right:
            high = i - 1
        else:
            low = i + 1
    raise ValueError("invalid k")


# --- BS-23 ---
def row_with_max_ones(mat: List[List[int]]) -> int:
    n = len(mat)
    m = len(mat[0]) if n else 0
    best_row, best_count = -1, 0
    for i, row in enumerate(mat):
        lb = lower_bound(row, 1)
        count = m - lb
        if count > best_count:
            best_count = count
            best_row = i
    return best_row if best_count else -1


# --- BS-24 ---
def search_matrix(matrix: List[List[int]], target: int) -> bool:
    n, m = len(matrix), len(matrix[0])
    low, high = 0, n * m - 1
    while low <= high:
        mid = low + (high - low) // 2
        val = matrix[mid // m][mid % m]
        if val == target:
            return True
        if val < target:
            low = mid + 1
        else:
            high = mid - 1
    return False


# --- BS-25 ---
def search_matrix_ii(matrix: List[List[int]], target: int) -> bool:
    n, m = len(matrix), len(matrix[0])
    row, col = 0, m - 1
    while row < n and col >= 0:
        val = matrix[row][col]
        if val == target:
            return True
        if val > target:
            col -= 1
        else:
            row += 1
    return False


# --- BS-26 ---
def find_peak_grid(mat: List[List[int]]) -> List[int]:
    n, m = len(mat), len(mat[0])
    low, high = 0, m - 1

    def max_in_col(c: int) -> int:
        r = 0
        for i in range(1, n):
            if mat[i][c] > mat[r][c]:
                r = i
        return r

    while low <= high:
        mid = low + (high - low) // 2
        row = max_in_col(mid)
        left = mat[row][mid - 1] if mid - 1 >= 0 else -1
        right = mat[row][mid + 1] if mid + 1 < m else -1
        if mat[row][mid] >= left and mat[row][mid] >= right:
            return [row, mid]
        if left > mat[row][mid]:
            high = mid - 1
        else:
            low = mid + 1
    return [-1, -1]


# --- BS-27 ---
def median_row_wise_sorted(mat: List[List[int]]) -> int:
    n, m = len(mat), len(mat[0])
    low = min(row[0] for row in mat)
    high = max(row[-1] for row in mat)
    need = (n * m) // 2

    def count_leq(x: int) -> int:
        return sum(upper_bound(row, x) for row in mat)

    while low <= high:
        mid = low + (high - low) // 2
        if count_leq(mid) <= need:
            low = mid + 1
        else:
            high = mid - 1
    return low


def _run_tests() -> None:
    assert binary_search([1, 3, 5, 7, 9], 7) == 3
    assert binary_search([1, 3, 5, 7, 9], 6) == -1
    assert lower_bound([1, 2, 2, 3], 2) == 1
    assert upper_bound([1, 2, 2, 3], 2) == 3
    assert search_insert([1, 3, 5, 6], 5) == 2
    assert search_insert([1, 3, 5, 6], 2) == 1
    assert floor_ceil([1, 2, 8, 10], 5) == (2, 8)
    assert floor_ceil([1, 2, 8, 10], 0) == (-1, 1)
    assert first_last_occurrence([2, 4, 6, 8, 8, 8, 11], 8) == (3, 5)
    assert count_occurrences([2, 4, 6, 8, 8, 8, 11], 8) == 3
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_rotated_duplicates([2, 5, 6, 0, 0, 1, 2], 0) is True
    assert search_rotated_duplicates([2, 5, 6, 0, 0, 1, 2], 3) is False
    assert find_min_rotated([4, 5, 6, 7, 0, 1, 2]) == 0
    assert find_min_rotated([3, 4, 5, 1, 2]) == 1
    assert rotation_count([4, 5, 6, 7, 0, 1, 2]) == 4
    assert rotation_count([1, 2, 3, 4]) == 0
    assert single_non_duplicate([1, 1, 2, 3, 3, 4, 4, 8, 8]) == 2
    assert single_non_duplicate([3, 3, 7, 7, 10, 11, 11]) == 10
    p = find_peak_element([1, 2, 3, 1])
    assert p == 2
    assert floor_sqrt(0) == 0 and floor_sqrt(1) == 1
    assert floor_sqrt(8) == 2 and floor_sqrt(36) == 6
    assert nth_root(3, 27) == 3 and nth_root(4, 69) == -1
    assert min_eating_speed([3, 6, 7, 11], 8) == 4
    assert min_days_bouquets([1, 10, 3, 10, 2], 3, 1) == 3
    assert min_days_bouquets([1, 10, 3, 10, 2], 3, 2) == -1
    assert smallest_divisor([1, 2, 5, 9], 6) == 5
    assert ship_within_days([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5) == 15
    assert find_kth_missing([2, 3, 4, 7, 11], 5) == 9
    assert aggressive_cows([1, 2, 8, 4, 9], 3) == 3
    assert allocate_books([12, 34, 67, 90], 2) == 113
    assert split_array_largest_sum([7, 2, 5, 10, 8], 2) == 18
    d = minmax_gas_station_distance([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 9)
    assert abs(d - 0.5) < 1e-3
    assert find_median_sorted_arrays([1, 3], [2]) == 2.0
    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
    assert kth_element_two_sorted([2, 3, 6, 7, 9], [1, 4, 8, 10], 5) == 6
    assert row_with_max_ones([[0, 0, 1], [0, 1, 1], [0, 0, 0]]) == 1
    assert search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3)
    assert not search_matrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13)
    assert search_matrix_ii(
        [
            [1, 4, 7, 11, 15],
            [2, 5, 8, 12, 19],
            [3, 6, 9, 16, 22],
            [10, 13, 14, 17, 24],
            [18, 21, 23, 26, 30],
        ],
        5,
    )
    peak = find_peak_grid([[1, 4], [3, 2]])
    r, c = peak
    val = [[1, 4], [3, 2]][r][c]
    assert val in (4, 3)
    assert median_row_wise_sorted([[1, 3, 5], [2, 6, 9], [3, 6, 9]]) == 5
    print("all tests passed")


if __name__ == "__main__":
    _run_tests()
