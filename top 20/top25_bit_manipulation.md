# Top 25 Bit Manipulation Interview Questions (C)

This file is created from the completed 40-problem handbook and contains only the requested top 25 questions.

Each question includes:
- Concept
- Theory / Intuition
- Full C Solution
- Complexity

---

## 1. Basic Bit Operations

### 1) Check if the i-th bit is set
**Concept:** Bit masking

**Theory / Intuition:** Build mask `1 << i` and AND with `n`. If result is non-zero, the i-th bit is set.

#### Full C Solution
```c
int isIthBitSet(unsigned int n, int i) {
    return (n & (1u << i)) != 0u;
}
```

**Complexity:** Time O(1), Space O(1)

---

### 2) Set the i-th bit
**Concept:** Bitwise OR

**Theory / Intuition:** OR with `1` at position `i` forces that bit to become 1.

#### Full C Solution
```c
unsigned int setIthBit(unsigned int n, int i) {
    return n | (1u << i);
}
```

**Complexity:** Time O(1), Space O(1)

---

### 3) Clear the i-th bit
**Concept:** AND with inverted mask

**Theory / Intuition:** `~(1 << i)` has zero at `i` and ones elsewhere. AND clears only that bit.

#### Full C Solution
```c
unsigned int clearIthBit(unsigned int n, int i) {
    return n & ~(1u << i);
}
```

**Complexity:** Time O(1), Space O(1)

---

### 4) Toggle the i-th bit
**Concept:** XOR

**Theory / Intuition:** XOR with 1 flips the bit; XOR with 0 keeps it unchanged.

#### Full C Solution
```c
unsigned int toggleIthBit(unsigned int n, int i) {
    return n ^ (1u << i);
}
```

**Complexity:** Time O(1), Space O(1)

---

### 5) Check if a number is odd or even using bits
**Concept:** Least significant bit (LSB)

**Theory / Intuition:** Odd numbers have LSB = 1; even numbers have LSB = 0.

#### Full C Solution
```c
int isOdd(int n) {
    return (n & 1) != 0;
}

int isEven(int n) {
    return (n & 1) == 0;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 2. Bit Tricks (Core Interview Patterns)

### 6) Check if a number is power of two
**Concept:** `n & (n - 1)` trick

**Theory / Intuition:** Power of two has exactly one set bit. Clearing rightmost set bit gives zero.

#### Full C Solution
```c
int isPowerOfTwo(int n) {
    return n > 0 && (n & (n - 1)) == 0;
}
```

**Complexity:** Time O(1), Space O(1)

---

### 7) Check if a number is power of four
**Concept:** Power-of-two + bit-position check

**Theory / Intuition:** Number must be power of two and its only set bit should be in even position (0, 2, 4, ...).

#### Full C Solution
```c
int isPowerOfFour(int n) {
    return n > 0 && (n & (n - 1)) == 0 && (n & 0x55555555) != 0;
}
```

**Complexity:** Time O(1), Space O(1)

---

### 8) Find the rightmost set bit
**Concept:** Two's complement trick

**Theory / Intuition:** `n & -n` isolates the lowest set bit.

#### Full C Solution
```c
unsigned int rightMostSetBit(unsigned int n) {
    return n & (~n + 1u);
}
```

**Complexity:** Time O(1), Space O(1)

---

### 9) Remove the rightmost set bit
**Concept:** Kernighan trick

**Theory / Intuition:** `n & (n - 1)` clears the lowest set bit.

#### Full C Solution
```c
unsigned int removeRightMostSetBit(unsigned int n) {
    return n & (n - 1u);
}
```

**Complexity:** Time O(1), Space O(1)

---

### 10) Count set bits (Brian Kernighan Algorithm)
**Concept:** Repeatedly clear lowest set bit

**Theory / Intuition:** Each iteration removes one set bit, so loop runs exactly popcount times.

#### Full C Solution
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

## 3. XOR Pattern Problems (Very Important)

### 11) Single number (all others appear twice)
**Concept:** XOR cancellation

**Theory / Intuition:** `a ^ a = 0` and `x ^ 0 = x`; all duplicates cancel.

#### Full C Solution
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

### 12) Two unique numbers (all others appear twice)
**Concept:** XOR partition

**Theory / Intuition:**
- XOR all numbers to get `x ^ y`.
- Find rightmost set bit in `x ^ y`.
- Partition numbers by this bit and XOR each group.

#### Full C Solution
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

### 13) Single number where others appear thrice
**Concept:** Bit counting modulo 3

**Theory / Intuition:** For each bit position, counts from triplicated numbers are multiples of 3. Remainder indicates unique number's bit.

#### Full C Solution
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

### 14) Find missing number (1..N)
**Concept:** XOR of expected and actual

**Theory / Intuition:** XOR `1..N` and all array values (size `N-1`). Equal numbers cancel, missing remains.

#### Full C Solution
```c
int missingNumber1toN(const int *a, int n) {
    // a has size n-1 and contains numbers from 1..n with one missing
    int xr = 0;

    for (int i = 1; i <= n; i++) {
        xr ^= i;
    }
    for (int i = 0; i < n - 1; i++) {
        xr ^= a[i];
    }

    return xr;
}
```

**Complexity:** Time O(n), Space O(1)

---

### 15) Find missing and duplicate number
**Concept:** XOR partition + verification

**Theory / Intuition:**
- XOR array with `1..n` gives `missing ^ duplicate`.
- Split by rightmost set bit to recover two candidates.
- Verify by scanning array to decide which is duplicate.

#### Full C Solution
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

## 4. Bit Manipulation on Numbers

### 16) Reverse bits of a 32-bit integer
**Concept:** Shift and rebuild

**Theory / Intuition:** Read LSB and append to result by shifting result left each step.

#### Full C Solution
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

### 17) Swap odd and even bits
**Concept:** Mask + shift + merge

**Theory / Intuition:**
- Extract odd-position bits and shift right.
- Extract even-position bits and shift left.
- OR both results.

#### Full C Solution
```c
unsigned int swapOddEvenBits(unsigned int x) {
    unsigned int odd = (x & 0xAAAAAAAAu) >> 1;
    unsigned int even = (x & 0x55555555u) << 1;
    return odd | even;
}
```

**Complexity:** Time O(1), Space O(1)

---

### 18) Minimum bit flips to convert A -> B
**Concept:** XOR + popcount

**Theory / Intuition:** Differing bits become 1 in `A ^ B`. Count the set bits.

#### Full C Solution
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

### 19) Next greater number with same number of set bits
**Concept:** SNOOB trick

**Theory / Intuition:**
- Isolate smallest set bit.
- Add it to create ripple.
- Rearrange trailing ones to smallest layout.

#### Full C Solution
```c
unsigned int nextHigherSameSetBits(unsigned int x) {
    if (x == 0u) {
        return 0u;
    }

    unsigned int smallest = x & (~x + 1u);
    unsigned int ripple = x + smallest;

    if (ripple == 0u) {
        // overflow in 32-bit space, no valid next value
        return 0u;
    }

    unsigned int ones = x ^ ripple;
    ones = (ones >> 2) / smallest;

    return ripple | ones;
}
```

**Complexity:** Time O(1), Space O(1)

---

## 5. Arithmetic Using Bits

### 20) Add two numbers without using +
**Concept:** XOR + carry propagation

**Theory / Intuition:** XOR gives sum without carry, AND gives carry bits; shift carry and repeat.

#### Full C Solution
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

### 21) Divide two integers without using / or *
**Concept:** Shift-subtract long division

**Theory / Intuition:** Try subtracting `divisor << i` from high bit to low bit and set quotient bit `i` when possible.

#### Full C Solution
```c
#include <limits.h>
#include <stdlib.h>

int divideNoSlashNoMul(int dividend, int divisor) {
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

## 6. Array Bit Manipulation

### 22) Minimum XOR pair in array
**Concept:** Sort + adjacent comparison

**Theory / Intuition:** In sorted order, minimum XOR pair is always among adjacent elements.

#### Full C Solution
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

**Complexity:** Time O(n log n), Space O(1) extra (in-place sort)

---

### 23) Sum of bit differences among all pairs
**Concept:** Per-bit contribution

**Theory / Intuition:** At each bit, if `ones` numbers have bit=1 and `zeros` have bit=0, differing ordered pairs contribute `2 * ones * zeros`.

#### Full C Solution
```c
long long sumBitDifferencesAllPairs(const int *a, int n) {
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

## 7. Bitmask / Subset Techniques

### 24) Generate subsets using bitmask
**Concept:** Bitmask enumeration

**Theory / Intuition:** Mask from `0` to `(1<<n)-1` encodes subset membership of each index.

#### Full C Solution
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

**Complexity:** Time O(n * 2^n), Space O(1) extra (excluding output)

---

### 25) Gray code generation
**Concept:** Binary to Gray transformation

**Theory / Intuition:** Gray value of `i` is `i ^ (i >> 1)`. Consecutive Gray codes differ by one bit.

#### Full C Solution
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
- Full sequence: Time O(2^bits), Space O(1) extra

---

## Quick Revision: Top Bit Tricks

| Trick | Meaning |
|---|---|
| `n & (n - 1)` | Remove rightmost set bit |
| `n & -n` | Isolate rightmost set bit |
| `x ^ x = 0` | XOR cancellation |
| `x << k` | Multiply by `2^k` (if no overflow) |
| `x >> k` | Divide by `2^k` for non-negative integers |

