# Topic 5 — Cache-Efficient Programming Interview Solutions (Q061-Q068)

## Q061: False-sharing detection and fix with padding
### 1. Problem Statement
Separate frequently updated fields into different cache lines.
### 2. Assumptions
- 64-byte cache line target.
### 3. Full C Code
```c
#include <stdalign.h>
#include <stdint.h>
#include <stdatomic.h>

typedef struct {
    alignas(64) _Atomic uint32_t producer_count;
    alignas(64) _Atomic uint32_t consumer_count;
} NoFalseSharingCounters;
```
### 4. Complexity
- O(1) access
### 5. Interview Follow-ups
1. Memory overhead tradeoff?
2. How do you validate improvement?

## Q062: Cache-line-aware struct layout optimization
### 1. Problem Statement
Group hot fields; isolate cold fields.
### 2. Assumptions
- Access frequency known from profiling.
### 3. Full C Code
```c
typedef struct {
    uint32_t state;
    uint32_t head;
    uint32_t tail;
} DriverHot;

typedef struct {
    uint8_t debug_blob[256];
    uint32_t error_hist[64];
} DriverCold;
```
### 4. Complexity
- No big-O change, better locality
### 5. Interview Follow-ups
1. ABI compatibility impact?
2. How often should layout be revisited?

## Q063: AoS-to-SoA conversion for sensor processing
### 1. Problem Statement
Convert array-of-struct to struct-of-arrays.
### 2. Assumptions
- Same element count and order.
### 3. Full C Code
```c
typedef struct {
    float x;
    float y;
    float z;
} Sample3D;

void aos_to_soa(const Sample3D *in, float *x, float *y, float *z, int n) {
    for (int i = 0; i < n; i++) {
        x[i] = in[i].x;
        y[i] = in[i].y;
        z[i] = in[i].z;
    }
}
```
### 4. Complexity
- O(n)
### 5. Interview Follow-ups
1. SIMD/vectorization benefits?
2. Cost of conversion step?

## Q064: Blocked matrix multiplication (cache-aware)
### 1. Problem Statement
Reduce cache misses in matrix multiply.
### 2. Assumptions
- Square matrices in row-major.
### 3. Full C Code
```c
void matmul_blocked(float *A, float *B, float *C, int n, int bs) {
    for (int ii = 0; ii < n; ii += bs) {
        for (int kk = 0; kk < n; kk += bs) {
            for (int jj = 0; jj < n; jj += bs) {
                for (int i = ii; i < ii + bs && i < n; i++) {
                    for (int k = kk; k < kk + bs && k < n; k++) {
                        float a = A[i * n + k];
                        for (int j = jj; j < jj + bs && j < n; j++) {
                            C[i * n + j] += a * B[k * n + j];
                        }
                    }
                }
            }
        }
    }
}
```
### 4. Complexity
- O(n^3) arithmetic, better cache behavior
### 5. Interview Follow-ups
1. How choose block size?
2. L1 vs L2 tuning approach?

## Q065: Prefetch-friendly traversal pattern
### 1. Problem Statement
Use linear access to improve cache hit rate.
### 2. Assumptions
- Data contiguous.
### 3. Full C Code
```c
int sum_linear_int(const int *a, int n) {
    int s = 0;
    for (int i = 0; i < n; i++) {
        s += a[i];
    }
    return s;
}
```
### 4. Complexity
- O(n)
### 5. Interview Follow-ups
1. Pointer-chasing penalty?
2. Software prefetch usefulness?

## Q066: Hot/cold data split in driver structs
### 1. Problem Statement
Separate frequently used runtime fields from rare debug/config data.
### 2. Assumptions
- API can pass pointers to both parts.
### 3. Full C Code
```c
typedef struct {
    uint32_t run_state;
    uint32_t rx_head;
    uint32_t rx_tail;
} DriverHotPart;

typedef struct {
    uint32_t error_log[128];
    uint8_t reserved_cfg[512];
} DriverColdPart;
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Serialization implications?
2. Thread ownership per part?

## Q067: Cache-aligned ring indices separation
### 1. Problem Statement
Avoid producer/consumer touching same cache line.
### 2. Assumptions
- Separate head and tail lines.
### 3. Full C Code
```c
typedef struct {
    alignas(64) uint32_t head;
    alignas(64) uint32_t tail;
    uint8_t *buf;
    uint32_t cap;
} AlignedRingIdx;
```
### 4. Complexity
- O(1)
### 5. Interview Follow-ups
1. Is 64 always correct?
2. Embedded SRAM cost tradeoff?

## Q068: L1/L2-aware block-size tuning micro-benchmark
### 1. Problem Statement
Find best block size empirically.
### 2. Assumptions
- Benchmark harness available.
### 3. Full C Code
```c
int pick_best_block(const int *cands, int m, int (*score_fn)(int)) {
    int best_bs = cands[0];
    int best_score = score_fn(best_bs);

    for (int i = 1; i < m; i++) {
        int s = score_fn(cands[i]);
        if (s > best_score) {
            best_score = s;
            best_bs = cands[i];
        }
    }
    return best_bs;
}
```
### 4. Complexity
- O(m * benchmark_cost)
### 5. Interview Follow-ups
1. Runtime vs compile-time tuning?
2. Input-shape sensitivity?
