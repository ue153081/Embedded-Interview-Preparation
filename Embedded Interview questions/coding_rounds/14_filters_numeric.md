# Filters & Numeric Helpers

**IDs:** C213–C218 (6 questions)  
**Focus:** Moving average, EWMA, debounce, median, slew, PID.

[← Back to category index](./README.md)

---

### C213 — Moving average

**Interview prompt:**  
Maintain average of last N samples in a ring.

**Implement:**
```c
void mav_init(mav_t *m, int *buf, size_t n);
void mav_push(mav_t *m, int sample);
int mav_get(const mav_t *m);
```

**Constraints / expectations:**
- Until filled define behavior
- Integer math

**Follow-ups:**
- Fixed-point
- Weighted

---

### C214 — EWMA / LPF (Tesla-style)

**Interview prompt:**  
Called at 10 Hz: y = 0.1*x + 0.9*y; initialize to first sample.

**Implement:**
```c
float lowPassSamples_10hz(float sample);
```

**Constraints / expectations:**
- First-call init
- No drift issues beyond float

**Follow-ups:**
- Fixed-point version
- α parameterization

---

### C215 — Binary debounce filter

**Interview prompt:**  
Require K consecutive equal samples before accepting new level.

**Implement:**
```c
int debounce_sample(int level);
```

**Constraints / expectations:**
- K configurable
- Return stable level

**Follow-ups:**
- Time-based vs count-based
- ISR usage

---

### C216 — Median of 3

**Interview prompt:**  
Return median of three readings to reject spikes.

**Implement:**
```c
int median3(int a, int b, int c);
```

**Constraints / expectations:**
- Branch-efficient OK
- Correct for duplicates

**Follow-ups:**
- Median of 5
- Sort network

---

### C217 — Slew / rate limit

**Interview prompt:**  
Limit how fast a setpoint can change per call.

**Implement:**
```c
int slew(int current, int target, int max_delta);
```

**Constraints / expectations:**
- Symmetric up/down or separate—doc
- Saturate

**Follow-ups:**
- Time-based slew
- Nonlinear

---

### C218 — PID step (fixed-point)

**Interview prompt:**  
Implement one PID iteration in Q-format without floats if possible.

**Implement:**
```c
int pid_step(pid_t *p, int setpoint, int measurement);
```

**Constraints / expectations:**
- Anti-windup basic
- Document gains format

**Follow-ups:**
- Derivative on measurement
- Feedforward

---


---

[← Back to category index](./README.md)
