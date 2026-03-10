# Bit Manipulation Interview Handbook (40 Problems)

This file is fully completed. Every problem includes:
- Concept
- Theory / Intuition
- Full C Solution
- Time and Space Complexity

Note: Code blocks are standalone snippets for interview prep. You can combine them into one `.c` file by adding shared headers at the top.

---

## 1) Check if i-th Bit is Set
**Concept:** Bit masking

**Theory / Intuition:** Build mask `1 << i` and AND with `n`. If result is non-zero, bit is set.

### Full C Solution
```c
int isIthBitSet(unsigned int n, int i) {
    return (n & (1u << i)) != 0u;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 2) Set the i-th Bit
**Concept:** Bitwise OR

**Theory / Intuition:** OR with `1` at position `i` forces that bit to become 1.

### Full C Solution
```c
unsigned int setIthBit(unsigned int n, int i) {
    return n | (1u << i);
}
```

**Complexity:** Time O(1), Space O(1)

---

## 3) Clear the i-th Bit
**Concept:** AND with inverted mask

**Theory / Intuition:** `~(1 << i)` has zero at `i` and ones elsewhere; AND clears only that bit.

### Full C Solution
```c
unsigned int clearIthBit(unsigned int n, int i) {
    return n & ~(1u << i);
}
```

**Complexity:** Time O(1), Space O(1)

---

## 4) Toggle the i-th Bit
**Concept:** XOR

**Theory / Intuition:** XOR with 1 flips a bit, XOR with 0 keeps it unchanged.

### Full C Solution
```c
unsigned int toggleIthBit(unsigned int n, int i) {
    return n ^ (1u << i);
}
```

**Complexity:** Time O(1), Space O(1)

---

## 5) Check Odd or Even
**Concept:** Least significant bit (LSB)

**Theory / Intuition:** Odd numbers have LSB = 1, even numbers have LSB = 0.

### Full C Solution
```c
int isOdd(int n) {
    return (n & 1) != 0;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 6) Multiply / Divide by 2
**Concept:** Bit shifting

**Theory / Intuition:** Left shift multiplies by 2; right shift divides by 2 for non-negative integers.

### Full C Solution
```c
int multiplyBy2(int n) {
    return n << 1;
}

int divideBy2NonNegative(int n) {
    return n >> 1;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 7) Check Power of Two
**Concept:** `n & (n - 1)` trick

**Theory / Intuition:** A power of two has exactly one set bit. Removing rightmost set bit gives zero.

### Full C Solution
```c
int isPowerOfTwo(int n) {
    return n > 0 && (n & (n - 1)) == 0;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 8) Check Power of Four
**Concept:** Power-of-two check + even bit position check

**Theory / Intuition:** Number must be a power of two and its single set bit must be in positions 0,2,4,...

### Full C Solution
```c
int isPowerOfFour(int n) {
    return n > 0 && (n & (n - 1)) == 0 && (n & 0x55555555) != 0;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 9) Rightmost Set Bit
**Concept:** Two's complement

**Theory / Intuition:** `n & -n` isolates the lowest set bit.

### Full C Solution
```c
unsigned int rightMostSetBit(unsigned int n) {
    return n & (~n + 1u);
}
```

**Complexity:** Time O(1), Space O(1)

---

## 10) Remove Rightmost Set Bit
**Concept:** Kernighan trick

**Theory / Intuition:** `n & (n - 1)` clears the lowest set bit.

### Full C Solution
```c
unsigned int removeRightMostSetBit(unsigned int n) {
    return n & (n - 1u);
}
```

**Complexity:** Time O(1), Space O(1)

---

## 11) Count Set Bits
**Concept:** Brian Kernighan algorithm

**Theory / Intuition:** Each iteration removes one set bit; loop runs exactly popcount times.

### Full C Solution
```c
int countSetBits(unsigned int n) {
    int c = 0;
    while (n) {
        n &= (n - 1u);
        c++;
    }
    return c;
}
```

**Complexity:** Time O(k), Space O(1), where `k` is number of set bits.

---

## 12) Count Set Bits from 1 to N
**Concept:** Pattern based counting with highest power of 2

**Theory / Intuition:**
- Let `2^x` be highest power of 2 <= `n`.
- Bits from `1` to `2^x - 1` contribute `x * 2^(x-1)`.
- MSB contribution from `2^x` to `n` is `n - 2^x + 1`.
- Recur on remainder `n - 2^x`.

### Full C Solution
```c
static int highestPowerOf2LE(int n) {
    int x = 0;
    while ((1LL << (x + 1)) <= n) {
        x++;
    }
    return x;
}

long long countBits1toN(int n) {
    if (n <= 0) {
        return 0;
    }

    int x = highestPowerOf2LE(n);
    int p = 1 << x;  // 2^x

    long long bitsTill2PowX = 1LL * x * (p >> 1);
    long long msbContribution = 1LL * (n - p + 1);
    int remainder = n - p;

    return bitsTill2PowX + msbContribution + countBits1toN(remainder);
}
```

**Complexity:** Time O(log n), Space O(log n) due to recursion.

---

## 13) Single Number (all others appear twice)
**Concept:** XOR cancellation

**Theory / Intuition:** `a ^ a = 0` and `x ^ 0 = x`; duplicate pairs cancel out.

### Full C Solution
```c
int singleNumber(const int *a, int n) {
    int x = 0;
    for (int i = 0; i < n; i++) {
        x ^= a[i];
    }
    return x;
}
```

**Complexity:** Time O(n), Space O(1)

---

## 14) Two Unique Numbers (all others appear twice)
**Concept:** XOR partition

**Theory / Intuition:**
- XOR of all numbers = `x ^ y` (two unique numbers).
- Find rightmost set bit in `x ^ y`; that bit differs between `x` and `y`.
- Partition array by that bit and XOR within each group.

### Full C Solution
```c
void twoUniqueNumbers(const int *a, int n, int *x, int *y) {
    int xr = 0;
    for (int i = 0; i < n; i++) {
        xr ^= a[i];
    }

    int rsb = xr & -xr;
    *x = 0;
    *y = 0;

    for (int i = 0; i < n; i++) {
        if (a[i] & rsb) {
            *x ^= a[i];
        } else {
            *y ^= a[i];
        }
    }
}
```

**Complexity:** Time O(n), Space O(1)

---

## 15) Single Number (all others appear thrice)
**Concept:** Bit counting modulo 3

**Theory / Intuition:** For each bit position, counts from triplicated numbers are multiples of 3. Remainder gives unique number's bit.

### Full C Solution
```c
int singleNumberThrice(const int *a, int n) {
    unsigned int res = 0;

    for (int i = 0; i < 32; i++) {
        int sum = 0;
        unsigned int bit = 1u << i;
        for (int j = 0; j < n; j++) {
            if (((unsigned int)a[j]) & bit) {
                sum++;
            }
        }
        if (sum % 3) {
            res |= bit;
        }
    }

    return (int)res;
}
```

**Complexity:** Time O(32*n) = O(n), Space O(1)

---

## 16) Missing Number (array has values 0..n, one missing)
**Concept:** XOR property

**Theory / Intuition:** XOR all indices and values; equal values cancel and missing value remains.

### Full C Solution
```c
int missingNumber0toN(const int *a, int n) {
    // Array size is n, numbers are from 0..n (one missing)
    int x = n;
    for (int i = 0; i < n; i++) {
        x ^= i;
        x ^= a[i];
    }
    return x;
}
```

**Complexity:** Time O(n), Space O(1)

---

## 17) Missing + Duplicate (array has 1..n, one missing and one repeated)
**Concept:** XOR partition + verification

**Theory / Intuition:**
- XOR all array values with `1..n`, result is `missing ^ duplicate`.
- Partition by any set bit to recover two candidates.
- Scan array once to determine which candidate is duplicate.

### Full C Solution
```c
void findMissingAndDuplicate(const int *a, int n, int *missing, int *duplicate) {
    int xr = 0;

    for (int i = 0; i < n; i++) {
        xr ^= a[i];
        xr ^= (i + 1);
    }

    int rsb = xr & -xr;
    int x = 0;
    int y = 0;

    for (int i = 0; i < n; i++) {
        if (a[i] & rsb) {
            x ^= a[i];
        } else {
            y ^= a[i];
        }

        if ((i + 1) & rsb) {
            x ^= (i + 1);
        } else {
            y ^= (i + 1);
        }
    }

    int xIsDuplicate = 0;
    for (int i = 0; i < n; i++) {
        if (a[i] == x) {
            xIsDuplicate = 1;
            break;
        }
    }

    if (xIsDuplicate) {
        *duplicate = x;
        *missing = y;
    } else {
        *duplicate = y;
        *missing = x;
    }
}
```

**Complexity:** Time O(n), Space O(1)

---

## 18) XOR of All Subarrays
**Concept:** Contribution counting

**Theory / Intuition:** `a[i]` appears in `(i+1)*(n-i)` subarrays. It contributes to XOR only if this count is odd.

### Full C Solution
```c
int xorOfAllSubarrays(const int *a, int n) {
    int res = 0;
    for (int i = 0; i < n; i++) {
        long long freq = 1LL * (i + 1) * (n - i);
        if (freq & 1LL) {
            res ^= a[i];
        }
    }
    return res;
}
```

**Complexity:** Time O(n), Space O(1)

---

## 19) XOR Range Query
**Concept:** Prefix XOR

**Theory / Intuition:** Similar to prefix sum. `xor(L..R) = prefix[R+1] ^ prefix[L]`.

### Full C Solution
```c
void buildPrefixXor(const int *a, int n, int *prefix) {
    // prefix size must be n+1
    prefix[0] = 0;
    for (int i = 0; i < n; i++) {
        prefix[i + 1] = prefix[i] ^ a[i];
    }
}

int xorRange(const int *prefix, int L, int R) {
    return prefix[R + 1] ^ prefix[L];
}
```

**Complexity:**
- Build: Time O(n), Space O(n)
- Query: Time O(1), Space O(1)

---

## 20) Reverse Bits (32-bit)
**Concept:** Shift and rebuild

**Theory / Intuition:** Read LSB of `n` repeatedly and append it to result's LSB after left shift.

### Full C Solution
```c
unsigned int reverseBits32(unsigned int n) {
    unsigned int r = 0;
    for (int i = 0; i < 32; i++) {
        r <<= 1;
        r |= (n & 1u);
        n >>= 1;
    }
    return r;
}
```

**Complexity:** Time O(32), Space O(1)

---

## 21) Swap Odd and Even Bits
**Concept:** Mask and shift

**Theory / Intuition:**
- Mask odd-position bits and shift right.
- Mask even-position bits and shift left.
- OR both shifted parts.

### Full C Solution
```c
unsigned int swapOddEvenBits(unsigned int x) {
    unsigned int odd = (x & 0xAAAAAAAAu) >> 1;
    unsigned int even = (x & 0x55555555u) << 1;
    return odd | even;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 22) Minimum Bit Flips (A -> B)
**Concept:** XOR + popcount

**Theory / Intuition:** Bits that differ become 1 in `A ^ B`. Count those 1s.

### Full C Solution
```c
int minBitFlips(int a, int b) {
    unsigned int x = (unsigned int)(a ^ b);
    int c = 0;
    while (x) {
        x &= (x - 1u);
        c++;
    }
    return c;
}
```

**Complexity:** Time O(k), Space O(1), where `k` is set bits in `a ^ b`.

---

## 23) Next Greater Number with Same Set Bits
**Concept:** SNOOB bit trick

**Theory / Intuition:**
- Isolate smallest set bit.
- Add it to create ripple.
- Rearrange trailing ones to smallest possible pattern.

### Full C Solution
```c
unsigned int nextHigherSameSetBits(unsigned int x) {
    if (x == 0u) {
        return 0u;
    }

    unsigned int smallest = x & (~x + 1u);
    unsigned int ripple = x + smallest;

    if (ripple == 0u) {
        // overflow: no higher number in 32-bit range
        return 0u;
    }

    unsigned int ones = x ^ ripple;
    ones = (ones >> 2) / smallest;

    return ripple | ones;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 24) Binary Palindrome
**Concept:** Two-pointer bit comparison

**Theory / Intuition:** Compare most significant and least significant used bits while moving inward.

### Full C Solution
```c
int isBinaryPalindrome(unsigned int n) {
    if (n == 0u) {
        return 1;
    }

    int left = 31;
    while (left > 0 && ((n >> left) & 1u) == 0u) {
        left--;
    }

    int right = 0;
    while (right < left) {
        unsigned int lb = (n >> left) & 1u;
        unsigned int rb = (n >> right) & 1u;
        if (lb != rb) {
            return 0;
        }
        left--;
        right++;
    }

    return 1;
}
```

**Complexity:** Time O(number of bits), Space O(1)

---

## 25) Add Without `+`
**Concept:** XOR + carry

**Theory / Intuition:**
- XOR gives partial sum without carry.
- AND gives carry positions; shift carry by one.
- Repeat until carry is zero.

### Full C Solution
```c
int addNoPlus(int a, int b) {
    while (b != 0) {
        unsigned int carry = ((unsigned int)(a & b)) << 1;
        a = a ^ b;
        b = (int)carry;
    }
    return a;
}
```

**Complexity:** Time O(1) for fixed-width integers, Space O(1)

---

## 26) Subtract Without `-`
**Concept:** Two's complement + add

**Theory / Intuition:** `a - b = a + (~b + 1)`.

### Full C Solution
```c
int addNoPlus(int a, int b);  // from previous problem

int subtractNoMinus(int a, int b) {
    return addNoPlus(a, addNoPlus(~b, 1));
}
```

**Complexity:** Time O(1), Space O(1)

---

## 27) Multiply Using Bits
**Concept:** Russian peasant multiplication

**Theory / Intuition:** Repeatedly add shifted multiplicand when current multiplier bit is 1.

### Full C Solution
```c
#include <stdlib.h>

long long multiplyUsingBits(int a, int b) {
    long long x = llabs((long long)a);
    long long y = llabs((long long)b);
    long long res = 0;

    while (y > 0) {
        if (y & 1LL) {
            res += x;
        }
        x <<= 1;
        y >>= 1;
    }

    if ((a < 0) ^ (b < 0)) {
        res = -res;
    }
    return res;
}
```

**Complexity:** Time O(log |b|), Space O(1)

---

## 28) Divide Without `/`
**Concept:** Shift-subtract long division

**Theory / Intuition:** Try subtracting `divisor << i` from highest bit to lowest bit and build quotient bits.

### Full C Solution
```c
#include <limits.h>
#include <stdlib.h>

int divideNoSlash(int dividend, int divisor) {
    if (divisor == 0) {
        return INT_MAX;
    }
    if (dividend == INT_MIN && divisor == -1) {
        return INT_MAX;
    }

    long long a = llabs((long long)dividend);
    long long b = llabs((long long)divisor);
    long long q = 0;

    for (int i = 31; i >= 0; i--) {
        if ((a >> i) >= b) {
            a -= (b << i);
            q |= (1LL << i);
        }
    }

    if ((dividend < 0) ^ (divisor < 0)) {
        q = -q;
    }

    return (int)q;
}
```

**Complexity:** Time O(32), Space O(1)

---

## 29) Compute `(7 * n) / 8`
**Concept:** Shift and subtract

**Theory / Intuition:** `7n = (8n - n) = (n << 3) - n`. Then divide by 8 using shift.

### Full C Solution
```c
int compute7nBy8(int n) {
    long long x = ((long long)n << 3) - n;

    // Ensure truncation toward 0 for negative values.
    if (x >= 0) {
        return (int)(x >> 3);
    }
    return (int)(-(((-x) >> 3)));
}
```

**Complexity:** Time O(1), Space O(1)

---

## 30) Minimum XOR Pair
**Concept:** Sorting + adjacent check

**Theory / Intuition:** In sorted order, minimum XOR pair must appear among adjacent elements.

### Full C Solution
```c
#include <limits.h>
#include <stdlib.h>

static int cmpIntAsc(const void *p1, const void *p2) {
    int a = *(const int *)p1;
    int b = *(const int *)p2;
    return (a > b) - (a < b);
}

int minimumXorPair(int *a, int n) {
    if (n < 2) {
        return -1;
    }

    qsort(a, (size_t)n, sizeof(int), cmpIntAsc);

    int best = INT_MAX;
    for (int i = 1; i < n; i++) {
        int v = a[i] ^ a[i - 1];
        if (v < best) {
            best = v;
        }
    }

    return best;
}
```

**Complexity:** Time O(n log n), Space O(1) extra (in-place sort).

---

## 31) XOR Sum of All Pairs
**Concept:** Bit contribution counting

**Theory / Intuition:** For each bit, it contributes to pair XOR when one number has bit=1 and the other has bit=0.

### Full C Solution
```c
long long xorSumAllPairs(const int *a, int n) {
    long long ans = 0;

    for (int bit = 0; bit < 32; bit++) {
        unsigned int mask = 1u << bit;
        long long ones = 0;

        for (int i = 0; i < n; i++) {
            if (((unsigned int)a[i]) & mask) {
                ones++;
            }
        }

        long long zeros = n - ones;
        ans += ones * zeros * (1LL << bit);
    }

    return ans;
}
```

**Complexity:** Time O(32*n) = O(n), Space O(1)

---

## 32) Sum of Bit Differences Among All Ordered Pairs
**Concept:** Per-bit zero/one counts

**Theory / Intuition:** At each bit, differing ordered pairs are `2 * ones * zeros`. Sum over all bits.

### Full C Solution
```c
long long sumBitDifferences(const int *a, int n) {
    long long ans = 0;

    for (int bit = 0; bit < 32; bit++) {
        unsigned int mask = 1u << bit;
        long long ones = 0;

        for (int i = 0; i < n; i++) {
            if (((unsigned int)a[i]) & mask) {
                ones++;
            }
        }

        long long zeros = n - ones;
        ans += 2LL * ones * zeros;
    }

    return ans;
}
```

**Complexity:** Time O(32*n) = O(n), Space O(1)

---

## 33) Count XOR Triplets
**Concept:** Prefix XOR observation

**Theory / Intuition:** For `i < j <= k`, if XOR of `a[i..k]` is 0, then any `j` between `i+1` and `k` is valid. Adds `(k - i)` triplets.

### Full C Solution
```c
long long countXorTriplets(const int *a, int n) {
    long long ans = 0;

    for (int i = 0; i < n; i++) {
        int xr = 0;
        for (int k = i; k < n; k++) {
            xr ^= a[k];
            if (xr == 0) {
                ans += (k - i);
            }
        }
    }

    return ans;
}
```

**Complexity:** Time O(n^2), Space O(1)

---

## 34) Generate All Subsets
**Concept:** Bitmask enumeration

**Theory / Intuition:** For `n` elements, masks from `0` to `(1<<n)-1` represent inclusion/exclusion of each element.

### Full C Solution
```c
#include <stdio.h>

void printSubsets(const int *a, int n) {
    int total = 1 << n;

    for (int mask = 0; mask < total; mask++) {
        printf("{");
        int first = 1;

        for (int i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                if (!first) {
                    printf(", ");
                }
                printf("%d", a[i]);
                first = 0;
            }
        }

        printf("}\n");
    }
}
```

**Complexity:** Time O(n * 2^n), Space O(1) extra (excluding output).

---

## 35) Gray Code
**Concept:** Binary-to-Gray conversion

**Theory / Intuition:** Gray code of integer `i` is `i ^ (i >> 1)`.

### Full C Solution
```c
int grayCodeValue(int n) {
    return n ^ (n >> 1);
}

void generateGrayCode(int bits, int *out) {
    int total = 1 << bits;
    for (int i = 0; i < total; i++) {
        out[i] = i ^ (i >> 1);
    }
}
```

**Complexity:**
- Single value: Time O(1), Space O(1)
- Sequence: Time O(2^bits), Space O(1) extra

---

## 36) Generalized Word Abbreviations
**Concept:** Bitmask skipping characters

**Theory / Intuition:** Bit `1` means abbreviate that character; count consecutive abbreviated chars as a number.

### Full C Solution
```c
#include <stdio.h>
#include <string.h>

void printWordAbbreviations(const char *word) {
    int n = (int)strlen(word);
    int total = 1 << n;

    for (int mask = 0; mask < total; mask++) {
        int run = 0;

        for (int i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                run++;
            } else {
                if (run > 0) {
                    printf("%d", run);
                    run = 0;
                }
                putchar(word[i]);
            }
        }

        if (run > 0) {
            printf("%d", run);
        }

        printf("\n");
    }
}
```

**Complexity:** Time O(n * 2^n), Space O(1) extra.

---

## 37) Minimum Developers to Cover All Skills
**Concept:** Skill bitmask dynamic programming

**Theory / Intuition:**
- Represent each person by skill bitmask.
- `dp[mask]` stores minimum team size to cover `mask`.
- For each person, update transitions to `mask | personMask`.
- Backtrack stored parent pointers to build team indices.

### Full C Solution
```c
#include <limits.h>
#include <stdlib.h>

typedef struct {
    int count;
    int prevMask;
    int pickedPerson;
} TeamState;

int minimumDevelopers(const int *peopleMask, int peopleCount, int skillCount, int *teamOut) {
    if (skillCount <= 0 || skillCount > 20) {
        return -1;
    }

    int maxMask = 1 << skillCount;
    const int INF = INT_MAX / 4;

    TeamState *dp = (TeamState *)malloc((size_t)maxMask * sizeof(TeamState));
    TeamState *next = (TeamState *)malloc((size_t)maxMask * sizeof(TeamState));
    if (!dp || !next) {
        free(dp);
        free(next);
        return -1;
    }

    for (int m = 0; m < maxMask; m++) {
        dp[m].count = INF;
        dp[m].prevMask = -1;
        dp[m].pickedPerson = -1;
    }
    dp[0].count = 0;

    for (int p = 0; p < peopleCount; p++) {
        for (int m = 0; m < maxMask; m++) {
            next[m] = dp[m];
        }

        int pm = peopleMask[p] & (maxMask - 1);

        for (int m = 0; m < maxMask; m++) {
            if (dp[m].count == INF) {
                continue;
            }

            int nm = m | pm;
            if (dp[m].count + 1 < next[nm].count) {
                next[nm].count = dp[m].count + 1;
                next[nm].prevMask = m;
                next[nm].pickedPerson = p;
            }
        }

        TeamState *tmp = dp;
        dp = next;
        next = tmp;
    }

    int full = maxMask - 1;
    if (dp[full].count == INF) {
        free(dp);
        free(next);
        return -1;
    }

    int size = 0;
    int mask = full;

    while (mask != 0) {
        teamOut[size++] = dp[mask].pickedPerson;
        mask = dp[mask].prevMask;
    }

    for (int i = 0; i < size / 2; i++) {
        int t = teamOut[i];
        teamOut[i] = teamOut[size - 1 - i];
        teamOut[size - 1 - i] = t;
    }

    free(dp);
    free(next);
    return size;
}
```

**Complexity:** Time O(peopleCount * 2^skillCount), Space O(2^skillCount)

---

## 38) N-Queens Using Bitmask
**Concept:** Column and diagonal masks

**Theory / Intuition:**
- `cols` tracks occupied columns.
- `diag` tracks occupied main diagonals.
- `antiDiag` tracks occupied anti-diagonals.
- Available spots are computed with bit operations each row.

### Full C Solution
```c
static int solveNQueensDfs(int cols, int diag, int antiDiag, int allMask) {
    if (cols == allMask) {
        return 1;
    }

    int available = allMask & ~(cols | diag | antiDiag);
    int count = 0;

    while (available) {
        int bit = available & -available;
        available -= bit;

        count += solveNQueensDfs(
            cols | bit,
            ((diag | bit) << 1) & allMask,
            (antiDiag | bit) >> 1,
            allMask
        );
    }

    return count;
}

int countNQueensSolutions(int n) {
    if (n <= 0 || n > 15) {
        return 0;
    }

    int allMask = (1 << n) - 1;
    return solveNQueensDfs(0, 0, 0, allMask);
}
```

**Complexity:** Roughly O(n!) worst-case, with strong pruning; Space O(n) recursion depth.

---

## 39) Sudoku Solver Using Bitmask
**Concept:** Row/column/box bitsets + backtracking

**Theory / Intuition:**
- Maintain 9-bit mask for each row, column, and 3x3 box.
- Candidate digits for cell = `~(row|col|box) & 0x1FF`.
- Use DFS and choose cell with minimum candidates for faster pruning.

### Full C Solution
```c
static int countBits9(int x) {
    int c = 0;
    while (x) {
        x &= (x - 1);
        c++;
    }
    return c;
}

static int solveSudokuDfs(char board[9][9], int row[9], int col[9], int box[9]) {
    int bestR = -1;
    int bestC = -1;
    int bestMask = 0;
    int minChoices = 10;

    for (int r = 0; r < 9; r++) {
        for (int c = 0; c < 9; c++) {
            if (board[r][c] != '.') {
                continue;
            }

            int b = (r / 3) * 3 + (c / 3);
            int used = row[r] | col[c] | box[b];
            int cand = (~used) & 0x1FF;
            int choices = countBits9(cand);

            if (choices == 0) {
                return 0;
            }

            if (choices < minChoices) {
                minChoices = choices;
                bestR = r;
                bestC = c;
                bestMask = cand;

                if (choices == 1) {
                    break;
                }
            }
        }
    }

    if (bestR == -1) {
        return 1;
    }

    int b = (bestR / 3) * 3 + (bestC / 3);

    for (int d = 0; d < 9; d++) {
        int bit = 1 << d;
        if ((bestMask & bit) == 0) {
            continue;
        }

        board[bestR][bestC] = (char)('1' + d);
        row[bestR] |= bit;
        col[bestC] |= bit;
        box[b] |= bit;

        if (solveSudokuDfs(board, row, col, box)) {
            return 1;
        }

        row[bestR] &= ~bit;
        col[bestC] &= ~bit;
        box[b] &= ~bit;
        board[bestR][bestC] = '.';
    }

    return 0;
}

int solveSudoku(char board[9][9]) {
    int row[9] = {0};
    int col[9] = {0};
    int box[9] = {0};

    for (int r = 0; r < 9; r++) {
        for (int c = 0; c < 9; c++) {
            if (board[r][c] == '.') {
                continue;
            }

            int d = board[r][c] - '1';
            if (d < 0 || d > 8) {
                return 0;
            }

            int bit = 1 << d;
            int b = (r / 3) * 3 + (c / 3);

            if ((row[r] & bit) || (col[c] & bit) || (box[b] & bit)) {
                return 0;
            }

            row[r] |= bit;
            col[c] |= bit;
            box[b] |= bit;
        }
    }

    return solveSudokuDfs(board, row, col, box);
}
```

**Complexity:** Exponential in number of empty cells (backtracking), Space O(empty cells).

---

## 40) Valid Words for Each Puzzle
**Concept:** Bitmask + subset enumeration

**Theory / Intuition:**
- Convert each word and puzzle into 26-bit masks.
- Valid word mask must include puzzle's first letter and be subset of puzzle mask.
- Enumerate all subsets of puzzle mask (excluding first letter) and sum frequencies.

### Full C Solution
```c
#include <stdlib.h>

static int toMask(const char *s) {
    int mask = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        int bit = s[i] - 'a';
        if (bit >= 0 && bit < 26) {
            mask |= (1 << bit);
        }
    }
    return mask;
}

static int popcountInt(int x) {
    int c = 0;
    while (x) {
        x &= (x - 1);
        c++;
    }
    return c;
}

static int cmpIntAsc2(const void *p1, const void *p2) {
    int a = *(const int *)p1;
    int b = *(const int *)p2;
    return (a > b) - (a < b);
}

static int freqLookup(const int *uniq, const int *freq, int n, int key) {
    int l = 0;
    int r = n - 1;

    while (l <= r) {
        int m = l + (r - l) / 2;
        if (uniq[m] == key) {
            return freq[m];
        }
        if (uniq[m] < key) {
            l = m + 1;
        } else {
            r = m - 1;
        }
    }

    return 0;
}

void validWordsForPuzzles(
    const char **words,
    int wordCount,
    const char **puzzles,
    int puzzleCount,
    int *out
) {
    int *masks = (int *)malloc((size_t)wordCount * sizeof(int));
    int m = 0;

    for (int i = 0; i < wordCount; i++) {
        int mask = toMask(words[i]);
        if (popcountInt(mask) <= 7) {
            masks[m++] = mask;
        }
    }

    qsort(masks, (size_t)m, sizeof(int), cmpIntAsc2);

    int *uniq = (int *)malloc((size_t)m * sizeof(int));
    int *freq = (int *)malloc((size_t)m * sizeof(int));
    int u = 0;

    for (int i = 0; i < m; i++) {
        if (u == 0 || masks[i] != uniq[u - 1]) {
            uniq[u] = masks[i];
            freq[u] = 1;
            u++;
        } else {
            freq[u - 1]++;
        }
    }

    for (int p = 0; p < puzzleCount; p++) {
        int pMask = toMask(puzzles[p]);
        int firstBit = 1 << (puzzles[p][0] - 'a');
        int rest = pMask & ~firstBit;

        int total = freqLookup(uniq, freq, u, firstBit);

        int subset = rest;
        while (subset) {
            int candidate = subset | firstBit;
            total += freqLookup(uniq, freq, u, candidate);
            subset = (subset - 1) & rest;
        }

        out[p] = total;
    }

    free(masks);
    free(uniq);
    free(freq);
}
```

**Complexity:**
- Preprocess words: O(W log W)
- Per puzzle: O(2^6 * log U), where `U` is unique mask count
- Total: O(W log W + P * 64 * log U)

---

## Key Bit Tricks Summary

| Trick | Meaning |
|---|---|
| `n & (n - 1)` | Remove rightmost set bit |
| `n & -n` | Isolate rightmost set bit |
| `x ^ x = 0` | XOR cancellation |
| `x ^ 0 = x` | XOR identity |
| `x << k` | Multiply by `2^k` (for non-overflowing integers) |
| `x >> k` | Divide by `2^k` for non-negative integers |
| `mask = 1 << i` | Build i-th bit mask |
| `x | mask` | Set bit |
| `x & ~mask` | Clear bit |
| `x ^ mask` | Toggle bit |

