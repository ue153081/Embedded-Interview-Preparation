# DSA Must-Do 30 — Complete C Solutions

Style: interview-ready C, clean indentation, edge cases included.

## M01) Two Sum
### Full C Code
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int key;
    int val;
    bool used;
} HashEntry;

static int hash_int(int x, int mod) {
    int h = x % mod;
    return (h < 0) ? h + mod : h;
}

bool two_sum(const int *nums, int n, int target, int *out_i, int *out_j) {
    int cap = 2 * n + 1;
    HashEntry *table = (HashEntry *)calloc((size_t)cap, sizeof(HashEntry));
    if (!table) return false;

    for (int i = 0; i < n; ++i) {
        int need = target - nums[i];
        int p = hash_int(need, cap);

        while (table[p].used) {
            if (table[p].key == need) {
                *out_i = table[p].val;
                *out_j = i;
                free(table);
                return true;
            }
            p = (p + 1) % cap;
        }

        p = hash_int(nums[i], cap);
        while (table[p].used) {
            p = (p + 1) % cap;
        }
        table[p].used = true;
        table[p].key = nums[i];
        table[p].val = i;
    }

    free(table);
    return false;
}
```
### Complexity
- Time: O(n) average
- Space: O(n)
### Interview Follow-ups
- Handle multiple valid pairs.
- Return all pairs without duplicates.

## M02) Best Time to Buy and Sell Stock
### Full C Code
```c
int max_profit(const int *prices, int n) {
    if (n <= 1) return 0;

    int min_price = prices[0];
    int best = 0;

    for (int i = 1; i < n; ++i) {
        if (prices[i] < min_price) {
            min_price = prices[i];
        } else {
            int profit = prices[i] - min_price;
            if (profit > best) best = profit;
        }
    }
    return best;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Unlimited transactions variant.
- Add cooldown or fee.

## M03) Maximum Subarray
### Full C Code
```c
int max_subarray(const int *nums, int n) {
    int cur = nums[0];
    int best = nums[0];

    for (int i = 1; i < n; ++i) {
        if (cur < 0) cur = nums[i];
        else cur += nums[i];
        if (cur > best) best = cur;
    }
    return best;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Return subarray boundaries too.

## M04) Product of Array Except Self
### Full C Code
```c
#include <stdlib.h>

int *product_except_self(const int *nums, int n) {
    int *out = (int *)malloc((size_t)n * sizeof(int));
    if (!out) return NULL;

    int prefix = 1;
    for (int i = 0; i < n; ++i) {
        out[i] = prefix;
        prefix *= nums[i];
    }

    int suffix = 1;
    for (int i = n - 1; i >= 0; --i) {
        out[i] *= suffix;
        suffix *= nums[i];
    }

    return out;
}
```
### Complexity
- Time: O(n)
- Space: O(1) extra (excluding output)
### Interview Follow-ups
- Overflow-safe variant using 64-bit.

## M05) Subarray Sum Equals K
### Full C Code
```c
#include <stdbool.h>
#include <stdlib.h>

typedef struct {
    int key;
    int val;
    bool used;
} PrefixMapEntry;

static int map_hash(int x, int mod) {
    int h = x % mod;
    return (h < 0) ? h + mod : h;
}

static int map_get(PrefixMapEntry *m, int cap, int key) {
    int p = map_hash(key, cap);
    while (m[p].used) {
        if (m[p].key == key) return m[p].val;
        p = (p + 1) % cap;
    }
    return 0;
}

static void map_add(PrefixMapEntry *m, int cap, int key, int delta) {
    int p = map_hash(key, cap);
    while (m[p].used && m[p].key != key) {
        p = (p + 1) % cap;
    }
    if (!m[p].used) {
        m[p].used = true;
        m[p].key = key;
        m[p].val = delta;
    } else {
        m[p].val += delta;
    }
}

int subarray_sum_equals_k(const int *nums, int n, int k) {
    int cap = 4 * n + 7;
    PrefixMapEntry *m = (PrefixMapEntry *)calloc((size_t)cap, sizeof(PrefixMapEntry));
    if (!m) return 0;

    int sum = 0;
    int ans = 0;
    map_add(m, cap, 0, 1);

    for (int i = 0; i < n; ++i) {
        sum += nums[i];
        ans += map_get(m, cap, sum - k);
        map_add(m, cap, sum, 1);
    }

    free(m);
    return ans;
}
```
### Complexity
- Time: O(n) average
- Space: O(n)
### Interview Follow-ups
- Longest subarray with sum K.

## M06) Move Zeroes
### Full C Code
```c
void move_zeroes(int *nums, int n) {
    int w = 0;
    for (int r = 0; r < n; ++r) {
        if (nums[r] != 0) {
            int t = nums[w];
            nums[w] = nums[r];
            nums[r] = t;
            w++;
        }
    }
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Stable non-zero order is preserved.

## M07) Rotate Array
### Full C Code
```c
static void reverse_range(int *a, int l, int r) {
    while (l < r) {
        int t = a[l];
        a[l] = a[r];
        a[r] = t;
        l++;
        r--;
    }
}

void rotate_array(int *nums, int n, int k) {
    if (n <= 1) return;
    k %= n;
    if (k < 0) k += n;

    reverse_range(nums, 0, n - 1);
    reverse_range(nums, 0, k - 1);
    reverse_range(nums, k, n - 1);
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Left-rotation with negative k.

## M08) Missing Number
### Full C Code
```c
int missing_number(const int *nums, int n) {
    int x = n;
    for (int i = 0; i < n; ++i) {
        x ^= i;
        x ^= nums[i];
    }
    return x;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Sum formula vs XOR overflow tradeoff.

## M09) Find the Duplicate Number
### Full C Code
```c
int find_duplicate(const int *nums, int n) {
    int slow = nums[0];
    int fast = nums[0];

    do {
        slow = nums[slow];
        fast = nums[nums[fast]];
    } while (slow != fast);

    slow = nums[0];
    while (slow != fast) {
        slow = nums[slow];
        fast = nums[fast];
    }
    return slow;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Why this maps to cycle detection.

## M10) Sort Colors
### Full C Code
```c
void sort_colors(int *nums, int n) {
    int lo = 0, mid = 0, hi = n - 1;

    while (mid <= hi) {
        if (nums[mid] == 0) {
            int t = nums[lo]; nums[lo] = nums[mid]; nums[mid] = t;
            lo++; mid++;
        } else if (nums[mid] == 1) {
            mid++;
        } else {
            int t = nums[mid]; nums[mid] = nums[hi]; nums[hi] = t;
            hi--;
        }
    }
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Generalize to k colors.

## M11) Valid Anagram
### Full C Code
```c
#include <stdbool.h>

bool is_anagram(const char *s, const char *t) {
    int cnt[256] = {0};

    for (int i = 0; s[i] != '\0'; ++i) {
        cnt[(unsigned char)s[i]]++;
    }
    for (int i = 0; t[i] != '\0'; ++i) {
        cnt[(unsigned char)t[i]]--;
    }
    for (int i = 0; i < 256; ++i) {
        if (cnt[i] != 0) return false;
    }
    return true;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Unicode handling strategy.

## M12) Group Anagrams
### Full C Code
```c
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char **items;
    int size;
    int cap;
    char key[128];
} AnaGroup;

static int cmp_char(const void *a, const void *b) {
    return (*(const char *)a - *(const char *)b);
}

static void make_key(const char *s, char *out, int out_cap) {
    int len = (int)strlen(s);
    if (len >= out_cap) len = out_cap - 1;
    memcpy(out, s, (size_t)len);
    out[len] = '\0';
    qsort(out, (size_t)len, sizeof(char), cmp_char);
}

int group_anagrams(char **strs, int n, AnaGroup **out_groups) {
    AnaGroup *groups = (AnaGroup *)calloc((size_t)n, sizeof(AnaGroup));
    if (!groups) return 0;

    int gcount = 0;

    for (int i = 0; i < n; ++i) {
        char key[128];
        make_key(strs[i], key, (int)sizeof(key));

        int g = -1;
        for (int j = 0; j < gcount; ++j) {
            if (strcmp(groups[j].key, key) == 0) {
                g = j;
                break;
            }
        }

        if (g == -1) {
            g = gcount++;
            strcpy(groups[g].key, key);
            groups[g].cap = 4;
            groups[g].items = (char **)malloc((size_t)groups[g].cap * sizeof(char *));
            groups[g].size = 0;
        }

        if (groups[g].size == groups[g].cap) {
            groups[g].cap *= 2;
            groups[g].items = (char **)realloc(groups[g].items,
                                               (size_t)groups[g].cap * sizeof(char *));
        }
        groups[g].items[groups[g].size++] = strs[i];
    }

    *out_groups = groups;
    return gcount;
}
```
### Complexity
- Time: O(n * k log k)
- Space: O(nk)
### Interview Follow-ups
- Optimize with frequency-signature key.

## M13) Valid Palindrome
### Full C Code
```c
#include <stdbool.h>

static bool is_alnum_char(char c) {
    return (c >= 'a' && c <= 'z') ||
           (c >= 'A' && c <= 'Z') ||
           (c >= '0' && c <= '9');
}

static char to_lower_char(char c) {
    if (c >= 'A' && c <= 'Z') return (char)(c - 'A' + 'a');
    return c;
}

bool is_palindrome(const char *s) {
    int l = 0;
    int r = 0;
    while (s[r] != '\0') r++;
    r--;

    while (l < r) {
        while (l < r && !is_alnum_char(s[l])) l++;
        while (l < r && !is_alnum_char(s[r])) r--;

        if (to_lower_char(s[l]) != to_lower_char(s[r])) return false;
        l++;
        r--;
    }
    return true;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Unicode-aware normalization.

## M14) Reverse Words in a String
### Full C Code
```c
#include <string.h>

static void rev(char *s, int l, int r) {
    while (l < r) {
        char t = s[l]; s[l] = s[r]; s[r] = t;
        l++; r--;
    }
}

void reverse_words(char *s) {
    int n = (int)strlen(s);
    int w = 0;

    for (int r = 0; r < n; ) {
        while (r < n && s[r] == ' ') r++;
        if (r >= n) break;

        if (w > 0) s[w++] = ' ';
        while (r < n && s[r] != ' ') s[w++] = s[r++];
    }
    s[w] = '\0';
    if (w == 0) return;

    rev(s, 0, w - 1);

    int start = 0;
    for (int i = 0; i <= w; ++i) {
        if (i == w || s[i] == ' ') {
            rev(s, start, i - 1);
            start = i + 1;
        }
    }
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Keep punctuation tokens intact.

## M15) String to Integer (atoi)
### Full C Code
```c
#include <limits.h>

int my_atoi(const char *s) {
    int i = 0;
    while (s[i] == ' ') i++;

    int sign = 1;
    if (s[i] == '+' || s[i] == '-') {
        if (s[i] == '-') sign = -1;
        i++;
    }

    long long v = 0;
    while (s[i] >= '0' && s[i] <= '9') {
        v = v * 10 + (s[i] - '0');
        long long signed_v = v * sign;
        if (signed_v > INT_MAX) return INT_MAX;
        if (signed_v < INT_MIN) return INT_MIN;
        i++;
    }

    return (int)(v * sign);
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Strict parsing vs permissive parsing.

## M16) Longest Substring Without Repeating Characters
### Full C Code
```c
int length_of_longest_substring(const char *s) {
    int last[256];
    for (int i = 0; i < 256; ++i) last[i] = -1;

    int best = 0;
    int l = 0;

    for (int r = 0; s[r] != '\0'; ++r) {
        unsigned char c = (unsigned char)s[r];
        if (last[c] >= l) l = last[c] + 1;
        last[c] = r;

        int len = r - l + 1;
        if (len > best) best = len;
    }
    return best;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- UTF-8 handling approach.

## M17) Longest Repeating Character Replacement
### Full C Code
```c
int character_replacement(const char *s, int k) {
    int freq[26] = {0};
    int l = 0;
    int maxf = 0;
    int best = 0;

    for (int r = 0; s[r] != '\0'; ++r) {
        int idx = s[r] - 'A';
        freq[idx]++;
        if (freq[idx] > maxf) maxf = freq[idx];

        while ((r - l + 1) - maxf > k) {
            freq[s[l] - 'A']--;
            l++;
        }

        int len = r - l + 1;
        if (len > best) best = len;
    }

    return best;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Lowercase + mixed charset.

## M18) Minimum Window Substring
### Full C Code
```c
#include <limits.h>
#include <string.h>

int min_window(const char *s, const char *t, int *out_l, int *out_len) {
    int need[256] = {0};
    int missing = 0;

    for (int i = 0; t[i] != '\0'; ++i) {
        need[(unsigned char)t[i]]++;
        missing++;
    }

    int l = 0;
    int best_l = -1;
    int best_len = INT_MAX;

    for (int r = 0; s[r] != '\0'; ++r) {
        unsigned char rc = (unsigned char)s[r];
        if (need[rc] > 0) missing--;
        need[rc]--;

        while (missing == 0) {
            int len = r - l + 1;
            if (len < best_len) {
                best_len = len;
                best_l = l;
            }

            unsigned char lc = (unsigned char)s[l++];
            need[lc]++;
            if (need[lc] > 0) missing++;
        }
    }

    if (best_l == -1) return 0;
    *out_l = best_l;
    *out_len = best_len;
    return 1;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Return actual substring without extra copy.

## M19) Find All Anagrams in a String
### Full C Code
```c
#include <stdlib.h>
#include <string.h>

int *find_anagrams(const char *s, const char *p, int *out_count) {
    int n = (int)strlen(s);
    int m = (int)strlen(p);
    *out_count = 0;
    if (m > n || m == 0) return NULL;

    int need[26] = {0};
    int win[26] = {0};

    for (int i = 0; i < m; ++i) {
        need[p[i] - 'a']++;
        win[s[i] - 'a']++;
    }

    int *ans = (int *)malloc((size_t)(n - m + 1) * sizeof(int));
    if (!ans) return NULL;

    if (memcmp(need, win, sizeof(need)) == 0) {
        ans[(*out_count)++] = 0;
    }

    for (int r = m; r < n; ++r) {
        win[s[r] - 'a']++;
        win[s[r - m] - 'a']--;

        if (memcmp(need, win, sizeof(need)) == 0) {
            ans[(*out_count)++] = r - m + 1;
        }
    }

    return ans;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- General charset size.

## M20) 3Sum
### Full C Code
```c
#include <stdlib.h>

typedef struct {
    int (*data)[3];
    int size;
    int cap;
} TripletList;

static int cmp_int(const void *a, const void *b) {
    int x = *(const int *)a;
    int y = *(const int *)b;
    return (x > y) - (x < y);
}

TripletList three_sum(int *nums, int n) {
    TripletList out = {0};
    qsort(nums, (size_t)n, sizeof(int), cmp_int);

    for (int i = 0; i < n; ++i) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;

        int l = i + 1;
        int r = n - 1;

        while (l < r) {
            long sum = (long)nums[i] + nums[l] + nums[r];
            if (sum < 0) {
                l++;
            } else if (sum > 0) {
                r--;
            } else {
                if (out.size == out.cap) {
                    out.cap = (out.cap == 0) ? 8 : out.cap * 2;
                    out.data = (int (*)[3])realloc(out.data,
                                                   (size_t)out.cap * sizeof(*out.data));
                }
                out.data[out.size][0] = nums[i];
                out.data[out.size][1] = nums[l];
                out.data[out.size][2] = nums[r];
                out.size++;

                l++;
                r--;
                while (l < r && nums[l] == nums[l - 1]) l++;
                while (l < r && nums[r] == nums[r + 1]) r--;
            }
        }
    }

    return out;
}
```
### Complexity
- Time: O(n^2)
- Space: O(1) extra (excluding output)
### Interview Follow-ups
- 4Sum and kSum recursion.

## M21) Two Sum II (Sorted Array)
### Full C Code
```c
#include <stdbool.h>

bool two_sum_sorted(const int *nums, int n, int target, int *i, int *j) {
    int l = 0;
    int r = n - 1;

    while (l < r) {
        long sum = (long)nums[l] + nums[r];
        if (sum == target) {
            *i = l;
            *j = r;
            return true;
        }
        if (sum < target) l++;
        else r--;
    }
    return false;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Return 1-based indices variant.

## M22) Remove Duplicates from Sorted Array
### Full C Code
```c
int remove_duplicates_sorted(int *nums, int n) {
    if (n == 0) return 0;

    int w = 1;
    for (int r = 1; r < n; ++r) {
        if (nums[r] != nums[w - 1]) {
            nums[w++] = nums[r];
        }
    }
    return w;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Allow at most twice variant.

## M23) Minimum Size Subarray Sum
### Full C Code
```c
#include <limits.h>

int min_subarray_len(int target, const int *nums, int n) {
    int l = 0;
    int sum = 0;
    int best = INT_MAX;

    for (int r = 0; r < n; ++r) {
        sum += nums[r];
        while (sum >= target) {
            int len = r - l + 1;
            if (len < best) best = len;
            sum -= nums[l++];
        }
    }

    return (best == INT_MAX) ? 0 : best;
}
```
### Complexity
- Time: O(n)
- Space: O(1)
### Interview Follow-ups
- Works only for positive numbers.

## M24) Binary Search
### Full C Code
```c
int binary_search_index(const int *nums, int n, int target) {
    int l = 0;
    int r = n - 1;

    while (l <= r) {
        int m = l + (r - l) / 2;
        if (nums[m] == target) return m;
        if (nums[m] < target) l = m + 1;
        else r = m - 1;
    }
    return -1;
}
```
### Complexity
- Time: O(log n)
- Space: O(1)
### Interview Follow-ups
- First/last occurrence variant.

## M25) Search in Rotated Sorted Array
### Full C Code
```c
int search_rotated(const int *nums, int n, int target) {
    int l = 0;
    int r = n - 1;

    while (l <= r) {
        int m = l + (r - l) / 2;
        if (nums[m] == target) return m;

        if (nums[l] <= nums[m]) {
            if (nums[l] <= target && target < nums[m]) {
                r = m - 1;
            } else {
                l = m + 1;
            }
        } else {
            if (nums[m] < target && target <= nums[r]) {
                l = m + 1;
            } else {
                r = m - 1;
            }
        }
    }
    return -1;
}
```
### Complexity
- Time: O(log n)
- Space: O(1)
### Interview Follow-ups
- Duplicates present variant.

## M26) Find First and Last Position of Element in Sorted Array
### Full C Code
```c
static int lower_bound_int(const int *a, int n, int target) {
    int l = 0;
    int r = n;
    while (l < r) {
        int m = l + (r - l) / 2;
        if (a[m] < target) l = m + 1;
        else r = m;
    }
    return l;
}

void search_range(const int *nums, int n, int target, int *out_first, int *out_last) {
    int lo = lower_bound_int(nums, n, target);
    if (lo == n || nums[lo] != target) {
        *out_first = -1;
        *out_last = -1;
        return;
    }

    int hi = lower_bound_int(nums, n, target + 1) - 1;
    *out_first = lo;
    *out_last = hi;
}
```
### Complexity
- Time: O(log n)
- Space: O(1)
### Interview Follow-ups
- Implement without helper function.

## M27) Valid Parentheses
### Full C Code
```c
#include <stdbool.h>
#include <stdlib.h>

bool is_valid_parentheses(const char *s) {
    int n = 0;
    while (s[n] != '\0') n++;

    char *st = (char *)malloc((size_t)n);
    if (!st) return false;

    int top = -1;

    for (int i = 0; i < n; ++i) {
        char c = s[i];
        if (c == '(' || c == '[' || c == '{') {
            st[++top] = c;
        } else {
            if (top < 0) {
                free(st);
                return false;
            }
            char t = st[top--];
            bool ok = (c == ')' && t == '(') ||
                      (c == ']' && t == '[') ||
                      (c == '}' && t == '{');
            if (!ok) {
                free(st);
                return false;
            }
        }
    }

    bool ans = (top == -1);
    free(st);
    return ans;
}
```
### Complexity
- Time: O(n)
- Space: O(n)
### Interview Follow-ups
- Stream processing (cannot store full input).

## M28) Daily Temperatures
### Full C Code
```c
#include <stdlib.h>

int *daily_temperatures(const int *temp, int n) {
    int *ans = (int *)calloc((size_t)n, sizeof(int));
    int *st = (int *)malloc((size_t)n * sizeof(int));
    if (!ans || !st) {
        free(ans);
        free(st);
        return NULL;
    }

    int top = -1;
    for (int i = 0; i < n; ++i) {
        while (top >= 0 && temp[i] > temp[st[top]]) {
            int idx = st[top--];
            ans[idx] = i - idx;
        }
        st[++top] = i;
    }

    free(st);
    return ans;
}
```
### Complexity
- Time: O(n)
- Space: O(n)
### Interview Follow-ups
- Strictly warmer vs warmer-or-equal.

## M29) Kth Largest Element in an Array
### Full C Code
```c
static void swap_int(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

static int partition_desc(int *a, int l, int r) {
    int pivot = a[r];
    int i = l;
    for (int j = l; j < r; ++j) {
        if (a[j] > pivot) {
            swap_int(&a[i], &a[j]);
            i++;
        }
    }
    swap_int(&a[i], &a[r]);
    return i;
}

int kth_largest(int *nums, int n, int k) {
    int target = k - 1;
    int l = 0;
    int r = n - 1;

    while (l <= r) {
        int p = partition_desc(nums, l, r);
        if (p == target) return nums[p];
        if (p < target) l = p + 1;
        else r = p - 1;
    }
    return -1;
}
```
### Complexity
- Time: O(n) average
- Space: O(1)
### Interview Follow-ups
- Deterministic pivot for worst-case guarantees.

## M30) Merge Intervals
### Full C Code
```c
#include <stdlib.h>

typedef struct {
    int start;
    int end;
} Interval;

typedef struct {
    Interval *arr;
    int size;
} IntervalList;

static int cmp_interval(const void *a, const void *b) {
    const Interval *x = (const Interval *)a;
    const Interval *y = (const Interval *)b;
    if (x->start != y->start) return x->start - y->start;
    return x->end - y->end;
}

IntervalList merge_intervals(Interval *in, int n) {
    IntervalList out = {0};
    if (n == 0) return out;

    qsort(in, (size_t)n, sizeof(Interval), cmp_interval);
    out.arr = (Interval *)malloc((size_t)n * sizeof(Interval));
    if (!out.arr) return out;

    out.arr[0] = in[0];
    out.size = 1;

    for (int i = 1; i < n; ++i) {
        Interval *last = &out.arr[out.size - 1];
        if (in[i].start <= last->end) {
            if (in[i].end > last->end) last->end = in[i].end;
        } else {
            out.arr[out.size++] = in[i];
        }
    }

    return out;
}
```
### Complexity
- Time: O(n log n)
- Space: O(n)
### Interview Follow-ups
- In-place compaction after sort.
