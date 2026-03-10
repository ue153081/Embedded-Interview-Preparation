# DSA Must-Do 30 - Complete Python Solutions + Theory

Style: interview-ready Python, clear logic, edge cases included.

## M01) Two Sum
### Theory / Intuition
- Scan once and store each value's index in a hash map.
- For each number `x`, check whether `target - x` has already appeared.
- This gives constant-time lookup on average, so total work is linear.

### Full Python Code
```python
from typing import List, Optional, Tuple


def two_sum(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return seen[need], i
        seen[x] = i
    return None
```

### Complexity
- Time: O(n) average
- Space: O(n)

### Interview Follow-ups
- Handle multiple valid pairs.
- Return all pairs without duplicates.

## M02) Best Time to Buy and Sell Stock
### Theory / Intuition
- Keep the minimum price seen so far.
- At each day, treat the current price as the sell price and compute profit.
- The best profit is the maximum of all such candidates.

### Full Python Code
```python
from typing import List


def max_profit(prices: List[int]) -> int:
    if len(prices) <= 1:
        return 0

    min_price = prices[0]
    best = 0

    for price in prices[1:]:
        if price < min_price:
            min_price = price
        else:
            best = max(best, price - min_price)

    return best
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Unlimited transactions variant.
- Add cooldown or fee.

## M03) Maximum Subarray
### Theory / Intuition
- Kadane's algorithm tracks the best subarray ending at each index.
- If extending the current subarray hurts (negative sum), start fresh.
- The global maximum over these local bests is the answer.

### Full Python Code
```python
from typing import List


def max_subarray(nums: List[int]) -> int:
    cur = nums[0]
    best = nums[0]

    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)

    return best
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Return subarray boundaries too.

## M04) Product of Array Except Self
### Theory / Intuition
- For each index, answer is `(product of elements left) * (product of elements right)`.
- Build left products in one pass into output.
- Multiply by running right product in reverse pass, no division needed.

### Full Python Code
```python
from typing import List


def product_except_self(nums: List[int]) -> List[int]:
    n = len(nums)
    out = [1] * n

    prefix = 1
    for i in range(n):
        out[i] = prefix
        prefix *= nums[i]

    suffix = 1
    for i in range(n - 1, -1, -1):
        out[i] *= suffix
        suffix *= nums[i]

    return out
```

### Complexity
- Time: O(n)
- Space: O(1) extra (excluding output)

### Interview Follow-ups
- Overflow-safe variant using 64-bit.

## M05) Subarray Sum Equals K
### Theory / Intuition
- Use prefix sums: if `prefix[j] - prefix[i] = k`, then subarray `(i+1..j)` sums to `k`.
- Rearranged: for current sum `s`, we need prior sums equal to `s - k`.
- Store frequency of each prefix sum in a hash map.

### Full Python Code
```python
from typing import List


def subarray_sum_equals_k(nums: List[int], k: int) -> int:
    freq = {0: 1}
    prefix = 0
    ans = 0

    for x in nums:
        prefix += x
        ans += freq.get(prefix - k, 0)
        freq[prefix] = freq.get(prefix, 0) + 1

    return ans
```

### Complexity
- Time: O(n) average
- Space: O(n)

### Interview Follow-ups
- Longest subarray with sum K.

## M06) Move Zeroes
### Theory / Intuition
- Maintain a write pointer for the next non-zero position.
- Scan with a read pointer; when non-zero appears, swap into write position.
- This keeps relative order of non-zeros and pushes zeroes to the end.

### Full Python Code
```python
from typing import List


def move_zeroes(nums: List[int]) -> None:
    w = 0
    for r in range(len(nums)):
        if nums[r] != 0:
            nums[w], nums[r] = nums[r], nums[w]
            w += 1
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Stable non-zero order is preserved.

## M07) Rotate Array
### Theory / Intuition
- Rotate right by `k` using three reversals.
- Reverse whole array, then reverse first `k`, then reverse the rest.
- This is in-place and avoids extra array allocation.

### Full Python Code
```python
from typing import List


def rotate_array(nums: List[int], k: int) -> None:
    n = len(nums)
    if n <= 1:
        return

    k %= n

    def reverse_range(l: int, r: int) -> None:
        while l < r:
            nums[l], nums[r] = nums[r], nums[l]
            l += 1
            r -= 1

    reverse_range(0, n - 1)
    reverse_range(0, k - 1)
    reverse_range(k, n - 1)
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Left-rotation with negative k.

## M08) Missing Number
### Theory / Intuition
- XOR all indices `0..n` and all array values.
- Equal values cancel out because `x ^ x = 0`.
- The remaining value is the missing number.

### Full Python Code
```python
from typing import List


def missing_number(nums: List[int]) -> int:
    x = len(nums)
    for i, v in enumerate(nums):
        x ^= i
        x ^= v
    return x
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Sum formula vs XOR overflow tradeoff.

## M09) Find the Duplicate Number
### Theory / Intuition
- Treat values as next pointers in a linked list (`i -> nums[i]`).
- Duplicate value creates a cycle.
- Floyd's tortoise-hare finds cycle entry, which is the duplicate.

### Full Python Code
```python
from typing import List


def find_duplicate(nums: List[int]) -> int:
    slow = nums[0]
    fast = nums[0]

    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break

    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]

    return slow
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Why this maps to cycle detection.

## M10) Sort Colors
### Theory / Intuition
- Dutch National Flag partitioning with three zones:
- `[0..lo-1]` are 0s, `[lo..mid-1]` are 1s, `[hi+1..end]` are 2s.
- Move `mid` through the array and swap into correct zones.

### Full Python Code
```python
from typing import List


def sort_colors(nums: List[int]) -> None:
    lo, mid, hi = 0, 0, len(nums) - 1

    while mid <= hi:
        if nums[mid] == 0:
            nums[lo], nums[mid] = nums[mid], nums[lo]
            lo += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[hi] = nums[hi], nums[mid]
            hi -= 1
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Generalize to k colors.

## M11) Valid Anagram
### Theory / Intuition
- Anagrams have identical character counts.
- Increment counts for one string and decrement for the other.
- If all counts return to zero, strings are anagrams.

### Full Python Code
```python
def is_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False

    count = {}
    for ch in s:
        count[ch] = count.get(ch, 0) + 1
    for ch in t:
        count[ch] = count.get(ch, 0) - 1
        if count[ch] < 0:
            return False

    return all(v == 0 for v in count.values())
```

### Complexity
- Time: O(n)
- Space: O(1) for fixed alphabet, else O(k)

### Interview Follow-ups
- Unicode handling strategy.

## M12) Group Anagrams
### Theory / Intuition
- Words that are anagrams share the same canonical key.
- Use sorted characters (or frequency tuple) as the hash key.
- Group words by this key in a dictionary.

### Full Python Code
```python
from collections import defaultdict
from typing import List


def group_anagrams(strs: List[str]) -> List[List[str]]:
    groups = defaultdict(list)

    for word in strs:
        key = "".join(sorted(word))
        groups[key].append(word)

    return list(groups.values())
```

### Complexity
- Time: O(n * k log k)
- Space: O(nk)

### Interview Follow-ups
- Optimize with frequency-signature key.

## M13) Valid Palindrome
### Theory / Intuition
- Use two pointers from both ends.
- Skip non-alphanumeric characters.
- Compare lowercased characters at both pointers.

### Full Python Code
```python
def is_palindrome(s: str) -> bool:
    l, r = 0, len(s) - 1

    while l < r:
        while l < r and not s[l].isalnum():
            l += 1
        while l < r and not s[r].isalnum():
            r -= 1

        if s[l].lower() != s[r].lower():
            return False

        l += 1
        r -= 1

    return True
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Unicode-aware normalization.

## M14) Reverse Words in a String
### Theory / Intuition
- Split by whitespace to normalize extra spaces.
- Reverse token order.
- Join with single spaces.

### Full Python Code
```python
def reverse_words(s: str) -> str:
    return " ".join(reversed(s.split()))
```

### Complexity
- Time: O(n)
- Space: O(n)

### Interview Follow-ups
- Keep punctuation tokens intact.

## M15) String to Integer (atoi)
### Theory / Intuition
- Parse in phases: trim leading spaces, parse optional sign, parse digits.
- Build numeric value digit by digit.
- Clamp to 32-bit signed range on overflow.

### Full Python Code
```python
def my_atoi(s: str) -> int:
    i = 0
    n = len(s)

    while i < n and s[i] == " ":
        i += 1

    sign = 1
    if i < n and s[i] in "+-":
        sign = -1 if s[i] == "-" else 1
        i += 1

    value = 0
    INT_MIN = -(2**31)
    INT_MAX = 2**31 - 1

    while i < n and s[i].isdigit():
        value = value * 10 + (ord(s[i]) - ord("0"))
        signed_value = sign * value
        if signed_value > INT_MAX:
            return INT_MAX
        if signed_value < INT_MIN:
            return INT_MIN
        i += 1

    return sign * value
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Strict parsing vs permissive parsing.

## M16) Longest Substring Without Repeating Characters
### Theory / Intuition
- Sliding window with left pointer `l` and right pointer `r`.
- Track last seen index of each character.
- If a repeated character appears inside window, move `l` past its previous index.

### Full Python Code
```python
def length_of_longest_substring(s: str) -> int:
    last = {}
    l = 0
    best = 0

    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1
        last[ch] = r
        best = max(best, r - l + 1)

    return best
```

### Complexity
- Time: O(n)
- Space: O(k)

### Interview Follow-ups
- UTF-8 handling approach.

## M17) Longest Repeating Character Replacement
### Theory / Intuition
- Keep a window where we can replace at most `k` chars to make all same.
- Required replacements in window = `window_size - max_frequency_char`.
- Shrink window when required replacements exceed `k`.

### Full Python Code
```python
def character_replacement(s: str, k: int) -> int:
    freq = [0] * 26
    l = 0
    maxf = 0
    best = 0

    for r, ch in enumerate(s):
        idx = ord(ch) - ord("A")
        freq[idx] += 1
        maxf = max(maxf, freq[idx])

        while (r - l + 1) - maxf > k:
            freq[ord(s[l]) - ord("A")] -= 1
            l += 1

        best = max(best, r - l + 1)

    return best
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Lowercase + mixed charset.

## M18) Minimum Window Substring
### Theory / Intuition
- Use a frequency map of required characters from `t`.
- Expand right pointer until all requirements are satisfied.
- Then shrink from left to get the smallest valid window.

### Full Python Code
```python
from collections import Counter


def min_window(s: str, t: str) -> str:
    if not s or not t:
        return ""

    need = Counter(t)
    missing = len(t)
    l = 0
    best_start = 0
    best_len = float("inf")

    for r, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1

        while missing == 0:
            window_len = r - l + 1
            if window_len < best_len:
                best_len = window_len
                best_start = l

            left_char = s[l]
            need[left_char] += 1
            if need[left_char] > 0:
                missing += 1
            l += 1

    if best_len == float("inf"):
        return ""
    return s[best_start:best_start + best_len]
```

### Complexity
- Time: O(n)
- Space: O(k)

### Interview Follow-ups
- Return indices instead of slicing.

## M19) Find All Anagrams in a String
### Theory / Intuition
- Use fixed-size sliding window of length `len(p)`.
- Compare character frequencies of window vs `p`.
- Update counts in O(1) per step by adding incoming char and removing outgoing char.

### Full Python Code
```python
from typing import List


def find_anagrams(s: str, p: str) -> List[int]:
    n, m = len(s), len(p)
    if m == 0 or m > n:
        return []

    need = [0] * 26
    win = [0] * 26

    for ch in p:
        need[ord(ch) - ord("a")] += 1

    ans = []

    for i, ch in enumerate(s):
        win[ord(ch) - ord("a")] += 1

        if i >= m:
            left_idx = ord(s[i - m]) - ord("a")
            win[left_idx] -= 1

        if i >= m - 1 and win == need:
            ans.append(i - m + 1)

    return ans
```

### Complexity
- Time: O(n) (alphabet size is constant)
- Space: O(1)

### Interview Follow-ups
- General charset size.

## M20) 3Sum
### Theory / Intuition
- Sort first so duplicate handling and two-pointer search become easy.
- Fix one number `nums[i]`, then solve two-sum on remaining range with pointers.
- Skip duplicates for `i`, `l`, and `r` to keep unique triplets.

### Full Python Code
```python
from typing import List


def three_sum(nums: List[int]) -> List[List[int]]:
    nums.sort()
    n = len(nums)
    out = []

    for i in range(n):
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                out.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
                while l < r and nums[r] == nums[r + 1]:
                    r -= 1

    return out
```

### Complexity
- Time: O(n^2)
- Space: O(1) extra (excluding output)

### Interview Follow-ups
- 4Sum and kSum recursion.

## M21) Two Sum II (Sorted Array)
### Theory / Intuition
- Since array is sorted, use two pointers at both ends.
- If sum is too small, move left pointer right.
- If sum is too large, move right pointer left.

### Full Python Code
```python
from typing import List, Optional, Tuple


def two_sum_sorted(nums: List[int], target: int) -> Optional[Tuple[int, int]]:
    l, r = 0, len(nums) - 1

    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            return l, r
        if s < target:
            l += 1
        else:
            r -= 1

    return None
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Return 1-based indices variant.

## M22) Remove Duplicates from Sorted Array
### Theory / Intuition
- Use write pointer `w` for next unique placement.
- Read pointer scans array once.
- Copy only when a new unique value appears.

### Full Python Code
```python
from typing import List


def remove_duplicates_sorted(nums: List[int]) -> int:
    if not nums:
        return 0

    w = 1
    for r in range(1, len(nums)):
        if nums[r] != nums[w - 1]:
            nums[w] = nums[r]
            w += 1

    return w
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Allow at most twice variant.

## M23) Minimum Size Subarray Sum
### Theory / Intuition
- Works for positive integers using sliding window.
- Expand window until sum reaches target, then shrink from left to minimize length.
- Track the minimum valid window seen.

### Full Python Code
```python
from typing import List


def min_subarray_len(target: int, nums: List[int]) -> int:
    l = 0
    total = 0
    best = float("inf")

    for r, x in enumerate(nums):
        total += x
        while total >= target:
            best = min(best, r - l + 1)
            total -= nums[l]
            l += 1

    return 0 if best == float("inf") else int(best)
```

### Complexity
- Time: O(n)
- Space: O(1)

### Interview Follow-ups
- Works only for positive numbers.

## M24) Binary Search
### Theory / Intuition
- Keep search range `[l, r]` on sorted data.
- Check middle element and discard half each step.
- Continue until found or range becomes empty.

### Full Python Code
```python
from typing import List


def binary_search_index(nums: List[int], target: int) -> int:
    l, r = 0, len(nums) - 1

    while l <= r:
        m = l + (r - l) // 2
        if nums[m] == target:
            return m
        if nums[m] < target:
            l = m + 1
        else:
            r = m - 1

    return -1
```

### Complexity
- Time: O(log n)
- Space: O(1)

### Interview Follow-ups
- First/last occurrence variant.

## M25) Search in Rotated Sorted Array
### Theory / Intuition
- At least one half of current range is always sorted.
- Detect sorted half and decide whether target lies inside it.
- Discard the other half each step.

### Full Python Code
```python
from typing import List


def search_rotated(nums: List[int], target: int) -> int:
    l, r = 0, len(nums) - 1

    while l <= r:
        m = l + (r - l) // 2
        if nums[m] == target:
            return m

        if nums[l] <= nums[m]:
            if nums[l] <= target < nums[m]:
                r = m - 1
            else:
                l = m + 1
        else:
            if nums[m] < target <= nums[r]:
                l = m + 1
            else:
                r = m - 1

    return -1
```

### Complexity
- Time: O(log n)
- Space: O(1)

### Interview Follow-ups
- Duplicates present variant.

## M26) Find First and Last Position of Element in Sorted Array
### Theory / Intuition
- Use binary search for lower bound (first index >= target).
- First position is lower bound of `target`.
- Last position is lower bound of `target + 1` minus one.

### Full Python Code
```python
from typing import List, Tuple


def search_range(nums: List[int], target: int) -> Tuple[int, int]:
    def lower_bound(x: int) -> int:
        l, r = 0, len(nums)
        while l < r:
            m = l + (r - l) // 2
            if nums[m] < x:
                l = m + 1
            else:
                r = m
        return l

    lo = lower_bound(target)
    if lo == len(nums) or nums[lo] != target:
        return -1, -1

    hi = lower_bound(target + 1) - 1
    return lo, hi
```

### Complexity
- Time: O(log n)
- Space: O(1)

### Interview Follow-ups
- Implement without helper function.

## M27) Valid Parentheses
### Theory / Intuition
- Opening brackets are pushed onto a stack.
- Closing bracket must match stack top type.
- Valid string ends with all matches consumed and empty stack.

### Full Python Code
```python
def is_valid_parentheses(s: str) -> bool:
    stack = []
    pairs = {")": "(", "]": "[", "}": "{"}

    for ch in s:
        if ch in "([{":
            stack.append(ch)
        else:
            if not stack or stack[-1] != pairs.get(ch):
                return False
            stack.pop()

    return not stack
```

### Complexity
- Time: O(n)
- Space: O(n)

### Interview Follow-ups
- Stream processing (cannot store full input).

## M28) Daily Temperatures
### Theory / Intuition
- Maintain a decreasing stack of indices by temperature.
- Current warmer day resolves answers for all smaller temps on top.
- Each index is pushed once and popped once.

### Full Python Code
```python
from typing import List


def daily_temperatures(temp: List[int]) -> List[int]:
    n = len(temp)
    ans = [0] * n
    stack = []  # indices with decreasing temperatures

    for i, t in enumerate(temp):
        while stack and t > temp[stack[-1]]:
            idx = stack.pop()
            ans[idx] = i - idx
        stack.append(i)

    return ans
```

### Complexity
- Time: O(n)
- Space: O(n)

### Interview Follow-ups
- Strictly warmer vs warmer-or-equal.

## M29) Kth Largest Element in an Array
### Theory / Intuition
- Quickselect partitions array around a pivot.
- After partition, pivot is in its final sorted position.
- Keep searching only the side containing index `k-1` in descending order.

### Full Python Code
```python
from typing import List


def kth_largest(nums: List[int], k: int) -> int:
    target = k - 1

    def partition(l: int, r: int) -> int:
        pivot = nums[r]
        i = l
        for j in range(l, r):
            if nums[j] > pivot:
                nums[i], nums[j] = nums[j], nums[i]
                i += 1
        nums[i], nums[r] = nums[r], nums[i]
        return i

    l, r = 0, len(nums) - 1
    while l <= r:
        p = partition(l, r)
        if p == target:
            return nums[p]
        if p < target:
            l = p + 1
        else:
            r = p - 1

    raise ValueError("k is out of range")
```

### Complexity
- Time: O(n) average, O(n^2) worst-case
- Space: O(1)

### Interview Follow-ups
- Deterministic pivot for worst-case guarantees.

## M30) Merge Intervals
### Theory / Intuition
- Sort intervals by start time.
- Iterate once and merge overlap with the last output interval.
- If no overlap, start a new interval.

### Full Python Code
```python
from typing import List


def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    if not intervals:
        return []

    intervals.sort(key=lambda x: (x[0], x[1]))
    merged = [intervals[0][:]]

    for start, end in intervals[1:]:
        last = merged[-1]
        if start <= last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])

    return merged
```

### Complexity
- Time: O(n log n)
- Space: O(n)

### Interview Follow-ups
- In-place compaction after sort.
