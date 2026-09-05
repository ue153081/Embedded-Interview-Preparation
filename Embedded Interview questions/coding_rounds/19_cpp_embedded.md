# C++ Embedded Coding

**IDs:** C261–C275 (15 questions)  
**Focus:** RAII, span, static ring, function_ref, expected, atomics, CRTP.

[← Back to category index](./README.md)

---

### C261 — RAII IRQ lock

**Interview prompt:**  
Implement a C++ RAII guard that disables IRQs in ctor and restores in dtor.

**Implement:**
```cpp
class IrqLock { public: IrqLock(); ~IrqLock(); IrqLock(const IrqLock&)=delete; /* ... */ };
```

**Constraints / expectations:**
- Nesting-safe restore
- No heap
- Rule of five lite

**Follow-ups:**
- Lock_guard mutex
- std::atomic signal

---

### C262 — Non-owning span

**Interview prompt:**  
Implement a simple Span<T> with data()/size()/subspan/bounds-checked at().

**Implement:**
```cpp
template<typename T> class Span { /* ... */ };
```

**Constraints / expectations:**
- No ownership
- Iterator optional

**Follow-ups:**
- vs std::span
- Lifetime safety

---

### C263 — Intrusive list template

**Interview prompt:**  
Intrusive doubly-linked list node mix-in and list operations.

**Implement:**
```cpp
template<typename T> struct IntrusiveNode { T* next; T* prev; };
template<typename T> class IntrusiveList { /* push/pop/erase */ };
```

**Constraints / expectations:**
- No alloc
- O(1) erase if node known

**Follow-ups:**
- Safe iteration while erase
- container_of style

---

### C264 — Static capacity ring (no heap)

**Interview prompt:**  
Template ring buffer with compile-time capacity, no dynamic allocation.

**Implement:**
```cpp
template<typename T, size_t N> class StaticRing {
 public:
  bool push(const T&); bool pop(T&);
};
```

**Constraints / expectations:**
- N power-of-two optional
- Trivial T first

**Follow-ups:**
- emplace
- ISR-safe policy

---

### C265 — function_ref without heap

**Interview prompt:**  
Non-owning callable reference for callbacks (store func ptr + obj).

**Implement:**
```cpp
template<typename Sig> class FunctionRef;
/* FunctionRef<void(int)> cb = ...; cb(3); */
```

**Constraints / expectations:**
- No alloc
- UB if referent dies—document

**Follow-ups:**
- vs std::function
- function_view

---

### C266 — unique_ptr custom deleter for DMA

**Interview prompt:**  
Manage DMA memory with unique_ptr and custom free.

**Implement:**
```cpp
struct DmaDeleter { void operator()(void* p) const; };
using DmaPtr = std::unique_ptr<uint8_t[], DmaDeleter>;
DmaPtr dma_make(size_t n);
```

**Constraints / expectations:**
- No leaks on exception if exceptions enabled—or document -fno-exceptions
- Alignment

**Follow-ups:**
- shared_ptr cache
- span from unique

---

### C267 — enum class + to_string

**Interview prompt:**  
Use enum class for modes; provide to_string and optional parse.

**Implement:**
```cpp
enum class Mode { Off, Run, Fault };
const char* to_string(Mode m);
```

**Constraints / expectations:**
- Exhaustive switch with warning
- Invalid handling

**Follow-ups:**
- std::optional parse
- Flag enums

---

### C268 — CRTP driver vs vtable

**Interview prompt:**  
Show a tiny driver interface with virtual calls and a CRTP version without vtable.

**Implement:**
```cpp
struct Uart { virtual int write(const uint8_t*, size_t)=0; virtual ~Uart()=default; };
template<typename Derived> struct UartCRTP { int write(...); };
```

**Constraints / expectations:**
- Discuss flash/RAM cost
- When vtable OK

**Follow-ups:**
- Concepts interface
- Fake for tests

---

### C269 — Move-only message queue

**Interview prompt:**  
Queue of move-only messages (e.g., unique_ptr payload).

**Implement:**
```cpp
template<typename T, size_t N> class MoveQueue {
 public:
  bool push(T&&); bool pop(T&);
};
```

**Constraints / expectations:**
- No copy of T
- Correct move on fail

**Follow-ups:**
- emplace
- ISR restrictions

---

### C270 — constexpr register encode

**Interview prompt:**  
Encode bitfields at compile time with constexpr functions.

**Implement:**
```cpp
constexpr uint32_t encode_ctrl(uint32_t div, bool en);
static_assert(encode_ctrl(3,true) == expected);
```

**Constraints / expectations:**
- No UB shifts
- Usable at compile time

**Follow-ups:**
- consteval
- Lookup tables

---

### C271 — Placement-new object pool

**Interview prompt:**  
Pool allocates objects via placement new; destroy explicitly.

**Implement:**
```cpp
template<typename T, size_t N> class ObjectPool {
 public:
  template<class...A> T* create(A&&...);
  void destroy(T*);
};
```

**Constraints / expectations:**
- Aligned storage
- No double destroy

**Follow-ups:**
- Exception safety
- Free list

---

### C272 — expected<T,E> lite

**Interview prompt:**  
Minimal success/error return without exceptions.

**Implement:**
```cpp
template<typename T, typename E> class Expected { /* ... */ };
Expected<int, Err> parse(const char*);
```

**Constraints / expectations:**
- bool conversion / has_value
- move semantics

**Follow-ups:**
- std::expected C++23
- Result monad

---

### C273 — Atomic flag handoff C++

**Interview prompt:**  
ISR sets atomic_bool with release; main loads acquire.

**Implement:**
```cpp
extern std::atomic_bool ready;
void isr();
void main_loop();
```

**Constraints / expectations:**
- Correct memory_order
- Data publication safety

**Follow-ups:**
- atomic<uint64_t>
- seq_cst tax

---

### C274 — Fix temporary lifetime callback bug

**Interview prompt:**  
Show a bug where a callback stores pointer to temporary; fix lifetimes.

**Implement:**
```cpp
void set_callback(std::function<void()> cb);
void buggy();
void fixed();
```

**Constraints / expectations:**
- Explain dangling
- Own or guarantee lifetime

**Follow-ups:**
- string_view pitfalls
- co_routines skip

---

### C275 — Header-only HAL traits

**Interview prompt:**  
Write a traits-based HAL selecting register access for real HW vs fake.

**Implement:**
```cpp
template<class Platform> struct UartHal { static void write(...); };
struct RealPlatform; struct FakePlatform;
```

**Constraints / expectations:**
- No virtual needed
- Test uses Fake

**Follow-ups:**
- Concepts constrain Platform
- Policy-based design

---


---

[← Back to category index](./README.md)
