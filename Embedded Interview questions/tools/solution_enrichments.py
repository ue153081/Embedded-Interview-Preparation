"""Rich interview-format content for coding-round solution generation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from generate_coding_solutions import Question

# ---------------------------------------------------------------------------
# C code beautifier — expands minified one-liners into readable interview code
# ---------------------------------------------------------------------------

def beautify_c_code(code: str) -> str:
    """Format compact C/C++ into multi-line interview style."""
    code = code.strip()
    if not code:
        return code

    nonempty = [ln for ln in code.splitlines() if ln.strip()]
    if len(nonempty) >= 6 and max(len(ln) for ln in nonempty) < 100:
        return code

    if code.startswith("#ifdef __KERNEL__"):
        return _beautify_kernel_block(code)

    out: list[str] = []
    depth = 0
    i = 0
    n = len(code)
    line = ""
    in_str = False
    str_ch = ""
    in_line_comment = False
    in_block_comment = False

    def flush_line() -> None:
        nonlocal line
        stripped = line.strip()
        if stripped:
            out.append("    " * depth + stripped)
        line = ""

    while i < n:
        ch = code[i]
        nxt = code[i + 1] if i + 1 < n else ""

        if in_block_comment:
            line += ch
            if ch == "*" and nxt == "/":
                line += "/"
                i += 2
                in_block_comment = False
                continue
            i += 1
            continue

        if in_line_comment:
            line += ch
            if ch == "\n":
                flush_line()
                in_line_comment = False
            i += 1
            continue

        if in_str:
            line += ch
            if ch == "\\" and nxt:
                line += nxt
                i += 2
                continue
            if ch == str_ch:
                in_str = False
            i += 1
            continue

        if ch == "/" and nxt == "/":
            flush_line()
            line = "//"
            in_line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            flush_line()
            line = "/*"
            in_block_comment = True
            i += 2
            continue
        if ch in "\"'":
            in_str = True
            str_ch = ch
            line += ch
            i += 1
            continue

        if ch == "{":
            if line.strip():
                out.append("    " * depth + line.strip() + " {")
            else:
                out.append("    " * depth + "{")
            depth += 1
            line = ""
            i += 1
            continue

        if ch == "}":
            if line.strip():
                flush_line()
            depth = max(0, depth - 1)
            out.append("    " * depth + "}")
            line = ""
            i += 1
            if nxt == ";":
                out[-1] += ";"
                i += 1
            continue

        if ch == ";":
            line += ch
            flush_line()
            i += 1
            continue

        if ch == "\n":
            if line.strip():
                flush_line()
            i += 1
            continue

        line += ch
        i += 1

    if line.strip():
        flush_line()

    result = "\n".join(out)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result


def _beautify_kernel_block(code: str) -> str:
    parts = code.split("#endif", 1)
    if len(parts) == 2:
        inner = beautify_c_code(parts[0].replace("#ifdef __KERNEL__", "", 1).strip())
        return f"#ifdef __KERNEL__\n{inner}\n#endif{parts[1]}"
    return code


def is_stub_code(code: str) -> bool:
    """Detect placeholder implementations."""
    compact = re.sub(r"\s+", "", code)
    if "Generation failed" in code:
        return True
    if re.search(r"\(void\)\w+;\s*\}", compact):
        return True
    if re.search(r"return 0;\s*\}\s*$", compact) and "{" in compact and compact.count("{") <= 2:
        if len(compact) < 80:
            return True
    if "see SOLUTION_CODE" in code or "see prompt" in code:
        return True
    if re.search(r"/\*.*stub.*\*/", code, re.I):
        return True
    return False


# ---------------------------------------------------------------------------
# Follow-up answer knowledge base (keyword -> substantive answer)
# ---------------------------------------------------------------------------

FOLLOWUP_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"isr|irq|interrupt", re.I),
     "Keep ISR to flag/clear/enqueue only; defer parsing, printf, and blocking to task context. "
     "Use `irq_save`/`irq_restore` or IRQ-safe atomics when both ISR and task touch shared state."),
    (re.compile(r"pow2|power.of.two", re.I),
     "Power-of-two capacity enables `(idx+1) & (cap-1)` indexing without division; "
     "tradeoff is sizing up to the next pow2 (up to ~2× waste)."),
    (re.compile(r"min.heap|heap", re.I),
     "Sorted list: O(n) insert, simple, good for <32 timers. Min-heap: O(log n) insert/pop, "
     "better for hundreds+. Timer wheel: O(1) amortized for coarse granularity."),
    (re.compile(r"periodic|drift", re.I),
     "Reschedule with `next += period` from an absolute anchor to avoid drift. "
     "If late, either catch up (burst fires) or skip missed beats and log `miss_count`."),
    (re.compile(r"aba", re.I),
     "Treiber stack suffers ABA without tagged pointers or epoch reclamation. "
     "Prefer Vyukov MPSC or a lock for production; document hazard domains."),
    (re.compile(r"unit test|table.test|test", re.I),
     "Table-test every state/event edge, plus fault injection for timeouts, NACK, and buffer full."),
    (re.compile(r"smp|mp safe|multiprocess", re.I),
     "Use acquire/release atomics, per-CPU data where possible; never use plain `volatile` as a lock substitute."),
    (re.compile(r"dma", re.I),
     "Cache-coherency: flush CPU writes before DMA TX; invalidate after DMA RX. "
     "Use `dma_alloc_coherent` on Linux or MPU non-cacheable regions on bare-metal."),
    (re.compile(r"wheel", re.I),
     "Hierarchical timer wheel (Linux-style) gives O(1) insert/tick for coarse timers; "
     "fine deadlines still need a min-heap or sorted list for sub-tick accuracy."),
    (re.compile(r"64.bit|jiffies", re.I),
     "Use `uint64_t` ticks when uptime exceeds wrap horizon. Linux `time_after(a,b)` uses signed "
     "difference on `unsigned long`; same trick works for 32-bit with max delta < 2³¹."),
    (re.compile(r"starvat", re.I),
     "Strict priority can starve low tasks; add time-slicing within priority or aging "
     "(boost priority after N ticks waiting)."),
    (re.compile(r"aging", re.I),
     "Increment a wait counter each scheduler tick; when it exceeds threshold, temporarily "
     "boost effective priority so long-waiting tasks eventually run."),
    (re.compile(r"complexity", re.I),
     "State Big-O for each API call; mention constant factors (cache lines, IRQ overhead) "
     "that dominate on embedded even when asymptotics look equal."),
    (re.compile(r"cache", re.I),
     "SoA vs AoS: SoA helps SIMD and sequential access; AoS is better for single-struct locality. "
     "Prefetch next cache line in hot loops; align to 32/64 B."),
    (re.compile(r"nack|arbitration", re.I),
     "On NACK: stop clock, generate STOP, return error. On arbitration loss: release bus, "
     "back off with random delay, retry up to N times."),
    (re.compile(r"non.block", re.I),
     "Return immediately with `EAGAIN` if TX ring full; caller polls or registers callback on drain."),
    (re.compile(r"flush|power.off", re.I),
     "Flush waits for TX shift register empty, not just ring drained. Before power-off, "
     "flush then disable TX IRQ to avoid stray bytes."),
    (re.compile(r"watchdog", re.I),
     "Pet watchdog only from a single supervised task after all critical loops ran; "
     "use a windowed watchdog (min/max pet interval) to catch runaway ISRs."),
    (re.compile(r"endian", re.I),
     "Wire format is usually big-endian (network); MCU memory is little-endian on ARM. "
     "Always use explicit `read_be16`/`write_le32` helpers, never cast packed structs pointers."),
    (re.compile(r"overlap|memmove", re.I),
     "`memcpy` is UB on overlap; `memmove` copies forward or backward depending on address order."),
    (re.compile(r"overflow|saturat", re.I),
     "Check before add/mul (`a > MAX - b`); return error or saturate and set sticky flag for telemetry."),
    (re.compile(r"tlsf|fragment", re.I),
     "TLSF gives O(1) alloc/free with low fragmentation for real-time; "
     "buddy allocator fragments less for power-of-two sizes but wastes space."),
    (re.compile(r"telemetry|metric", re.I),
     "Expose counters via sysfs/debugfs or a ring of events; rate-limit logging to avoid "
     "feedback loops that worsen the fault."),
    (re.compile(r"priority", re.I),
     "Bitmap + CLZ finds highest ready priority in O(1) for ≤32 levels; "
     "separate ready lists per priority for O(1) insert."),
    (re.compile(r"mutex|spinlock", re.I),
     "Spinlock for ISR/task short sections; mutex (sleeping) only in thread context. "
     "Never hold spinlock across blocking calls."),
    (re.compile(r"poll|select|epoll", re.I),
     "`poll_wait` adds fd to wait queue; ISR wakes via `wake_up_interruptible` when data ready."),
    (re.compile(r"ioctl", re.I),
     "Validate `_IOC_TYPE` and size; copy args with `copy_from_user`; return `-EFAULT`/`-EINVAL` on bad access."),
    (re.compile(r"uaccess|copy_to_user", re.I),
     "Always validate user buffer size; use `copy_to_user`/`get_user`; never dereference `__user` pointers directly."),
    (re.compile(r"of_property|device.tree|dt", re.I),
     "Parse with `of_property_read_u32`; check `-EINVAL`; use `devm_kzalloc` for probe-lifetime memory."),
    (re.compile(r"pm_runtime|suspend|resume", re.I),
     "Balance `pm_runtime_get/put`; in suspend save device state and gate clocks; resume restores registers."),
    (re.compile(r"mmap", re.I),
     "`remap_pfn_range` maps physical pages; set `VM_IO | VM_DONTEXPAND`; validate size against buffer."),
    (re.compile(r"exception|raii", re.I),
     "Disable exceptions on embedded; use `expected<T,E>` or error codes. RAII guards release DMA/locks on scope exit."),
    (re.compile(r"crtp", re.I),
     "CRTP avoids vtable dispatch — calls resolve at compile time; use when polymorphism is static per device type."),
    (re.compile(r"constexpr", re.I),
     "Compile-time register masks catch typos early; keeps hot paths free of runtime bit math."),
    (re.compile(r"fake|mock|harness", re.I),
     "Inject HAL fakes behind function pointers; record call order and args for regression tests on host."),
    (re.compile(r"backtrace|crash", re.I),
     "Capture LR/PC/stack in fault handler; use `.noinit` ram console or post-mortem dump over UART."),
    (re.compile(r"ring|buffer|full", re.I),
     "Define drop-newest vs drop-oldest vs block policy explicitly; count drops for diagnostics."),
    (re.compile(r"resync|framing|parser", re.I),
     "On bad CRC/sync, enter hunt mode scanning for magic byte; cap scan length to bound CPU in noise."),
    (re.compile(r"debounc", re.I),
     "Restart timer on each edge; fire only after quiet period. Separate timers for press vs release if needed."),
    (re.compile(r"pwm", re.I),
     "Share timer channel: one-shot for protocol timeouts, PWM via alternate compare mode — "
     "mutually exclusive via HAL mutex."),
    (re.compile(r"half.duplex|rs485", re.I),
     "Assert DE (driver enable) before TX, deassert after TX-complete IRQ, not after ring enqueue."),
    (re.compile(r"scatter|gather", re.I),
     "Build descriptor list in RAM; program first desc; chain `next` pointers; IRQ on last completion."),
    (re.compile(r"circular|double.buffer", re.I),
     "Ping-pong buffers: DMA fills inactive half while CPU processes active; swap on half-complete IRQ."),
    (re.compile(r"filter|iir|fir", re.I),
     "FIR: stable, linear phase, higher tap count. IIR: fewer taps, watch limit cycles and coefficient quantization."),
    (re.compile(r"fixed.point|q\d+", re.I),
     "Use 32-bit Q16.16; guard shifts; saturate on overflow; verify with float reference offline."),
    (re.compile(r"ipc|mailbox|rpmsg", re.I),
     "Shared memory + doorbell IRQ; use cache-line alignment and memory barriers; version the message header."),
    (re.compile(r"boot|handshake", re.I),
     "Sequence: reset hold → load vectors → release reset → wait for alive token with timeout and retry budget."),
    (re.compile(r"ecc|crc|checksum", re.I),
     "CRC catches bursty errors; add sequence numbers for duplication; ECC for NAND/NOR at driver layer."),
    (re.compile(r"branchless", re.I),
     "Use masks and arithmetic for predictable cycles; measure — modern branch predictors often beat clever hacks."),
    (re.compile(r"prefetch", re.I),
     "`__builtin_prefetch(p+stride, 0, 3)` one iteration ahead; align base to cache line."),
    (re.compile(r"unroll", re.I),
     "Manual unroll by 4 reduces loop overhead; stop when I-cache pressure reverses the gain."),
    (re.compile(r"soa|aos", re.I),
     "SoA for vectorized math (3-axis IMU); AoS when processing one sample at a time with all fields."),
    (re.compile(r"hash.collision", re.I),
     "Chaining handles collisions; cap bucket depth; rehash if load factor exceeds threshold."),
    (re.compile(r"accuracy", re.I),
     "Wheel quantizes to slot size; combine coarse wheel + fine heap for sub-ms deadlines."),
    (re.compile(r"skipped.beat", re.I),
     "Track `late_count`; policy: skip to `now + period` vs fire back-to-back catch-up — document choice."),
    (re.compile(r"phase.align", re.I),
     "Anchor `next` to global epoch (`next = epoch + k*period`) so multiple tasks stay in phase."),
    (re.compile(r"linux.*history|timer wheel history", re.I),
     "Classic Linux cascades timers between wheels on tick; hrtimers use rbtree for precise deadlines."),
    (re.compile(r"multiple.channel", re.I),
     "One HW timer channel per compare register; software mux if channels exhausted; document priority."),
    (re.compile(r"high.water", re.I),
     "Callback when ring crosses 75% full so producer can throttle before drops occur."),
    (re.compile(r"tx complete", re.I),
     "Fire callback from TX-empty ISR after last byte left shift register, not when queued to ring."),
    (re.compile(r"break signal", re.I),
     "Hold TX line low longer than one frame time; restore UART config afterward."),
    (re.compile(r"framing|overrun", re.I),
     "Read and clear error flags in ISR; count in stats; optionally flush RX FIFO on overrun."),
    (re.compile(r"clock.stretch", re.I),
     "Poll stretch flag with timeout; on timeout call bus recovery (clock 9 pulses + STOP)."),
    (re.compile(r"bus.recover", re.I),
     "Toggle SCL up to 9 times while SDA high, then generate STOP to release stuck slave."),
    (re.compile(r"gpio.*debounc|both press", re.I),
     "Separate debounce timers for press and release edges; symmetric timing reduces chatter on both transitions."),
    (re.compile(r"power cost", re.I),
     "One-shot HW compare lets CPU sleep between edges; periodic tick wastes power if events are sparse."),
    (re.compile(r"feasibility|wcet|schedul", re.I),
     "Sum WCETs ≤ period for naive test; use RTA (response-time analysis) for priorities and blocking."),
    (re.compile(r"what to do on miss", re.I),
     "Log miss, increment counter, optionally safe-state (degrade mode); never silently ignore safety deadlines."),
    (re.compile(r"stack", re.I),
     "Each task needs isolated stack; measure high-water with fill pattern; place stacks in MPU guard regions."),
    (re.compile(r"add priorit", re.I),
     "Insert ready queue per priority; pick highest non-empty; within level use round-robin."),
    (re.compile(r"drift.free", re.I),
     "Fire at `anchor + n*period`; never `last_fire + period` which accumulates handler runtime."),
    (re.compile(r"vs min.heap|vs list", re.I),
     "List wins below ~16 timers; heap wins 16–500; wheel wins for many coarse timeouts with rare cancel."),
    (re.compile(r"cancel.*callback|race.safe", re.I),
     "Use `active` flag + generation counter; in callback check generation before reschedule; "
     "`cancel_sync` waits for callback exit via semaphore."),
    (re.compile(r"debugfs|sysfs", re.I),
     "Sysfs for config; debugfs for bulky dumps; use `DEVICE_ATTR`/`debugfs_create_u32` patterns."),
    (re.compile(r"module.param", re.I),
     "`module_param` with `perm` 0644; validate under spinlock; document in `MODULE_PARM_DESC`."),
    (re.compile(r"threaded.irq", re.I),
     "Top half wakes thread; bottom half can sleep (I2C, SPI); keep top half <10 µs."),
    (re.compile(r"miscdevice", re.I),
     "`misc_register` for simple char dev; single open optional; use dynamic minor."),
    (re.compile(r"platform.driver", re.I),
     "`platform_driver` + `of_match_table`; probe gets resources via `devm_*`; remove reverses enable order."),
]


def followup_answer(fu: str, q: "Question") -> str:
    for pat, ans in FOLLOWUP_PATTERNS:
        if pat.search(fu):
            return ans
    title = q.title.lower()
    if "ring" in title:
        return (
            f"For {q.title}: document SPSC vs MPSC topology, full/empty semantics, "
            "and whether ISR or task owns each index."
        )
    if "uart" in title or "spi" in title or "i2c" in title:
        return (
            f"For {q.title}: specify timeout units, error recovery (NACK/overrun), "
            "and whether API is blocking or callback-driven."
        )
    return (
        f"For {q.title}: state the invariant you protect, measure worst-case latency, "
        f"then optimize — '{fu}' trades complexity vs determinism; pick based on N and IRQ rate."
    )


# ---------------------------------------------------------------------------
# Problem-specific clarifying questions
# ---------------------------------------------------------------------------

def clarifying_questions(q: "Question") -> list[str]:
    title = q.title.lower()
    prompt = q.prompt.lower()
    bullets: list[str] = []

    if "ring" in title or "queue" in title or "buffer" in title:
        bullets += [
            "Is capacity `cap` bytes with one spare slot, or fully usable `cap` bytes?",
            "Producer in ISR and consumer in task (SPSC), or different topology?",
        ]
    if "timer" in title or "schedul" in title or q.category == "timers":
        bullets += [
            "What tick resolution and wrap period does the HW timer provide?",
            "Should callbacks run in ISR context or a deferred worker thread?",
        ]
    if "uart" in title or "spi" in title or "i2c" in title:
        bullets += [
            "Is the controller memory-mapped with status flags as shown, or should I stub HAL hooks?",
            "What timeout units and max clock-stretch should I assume for bus recovery?",
        ]
    if "dma" in title or q.category == "dma":
        bullets += [
            "Is the buffer cache-coherent, or do I need explicit flush/invalidate?",
            "Single-shot or circular descriptor chain?",
        ]
    if "fsm" in title or "state" in title or q.category == "fsm":
        bullets += [
            "Should invalid inputs be ignored silently or counted for diagnostics?",
            "Do we need entry/exit actions per state, or pure transition function?",
        ]
    if "parser" in title or "protocol" in title or "frame" in title:
        bullets += [
            "Fixed frame length or length-prefix/CRC delimited?",
            "Byte-at-a-time ISR feed or blocking read with timeout?",
        ]
    if "pool" in title or "alloc" in title or q.category == "allocators":
        bullets += [
            "Fixed block size or variable? Is free allowed from ISR?",
            "Should exhaustion return NULL or a dedicated error code?",
        ]
    if "mutex" in title or "spinlock" in title or "atomic" in title or q.category == "sync":
        bullets += [
            "Can this lock be taken from ISR, or task-only?",
            "Single-core UP or SMP with preemptible kernel?",
        ]
    if "linux" in q.category or "driver" in title and "linux" in prompt:
        bullets += [
            "Target kernel version and GPL context — module snippet or pseudo-code OK?",
        ]
    if "cpp" in q.category or q.lang == "cpp":
        bullets += [
            "Which C++ standard (C++14/17) and are exceptions/RTTI enabled?",
        ]
    if "filter" in title or "crc" in title or "checksum" in title:
        bullets += [
            "Bit width and polynomial for CRC? Table-driven or bit-by-bit?",
        ]
    if "ipc" in title or "mailbox" in title or "dual" in title:
        bullets += [
            "Shared SRAM with cache coherency handled, or explicit flush?",
            "Ordering: doorbell IRQ after payload visible?",
        ]
    if "watchdog" in title or "reset" in title:
        bullets += [
            "Windowed watchdog (min/max pet interval) or simple countdown?",
        ]
    if "mem" in title and ("cpy" in title or "move" in title or "set" in title):
        bullets += [
            "May source and destination overlap? Alignment assumptions on buffers?",
        ]

    bullets += [
        f"Should the solution target bare-metal, or is POSIX/Linux acceptable for {q.title}?",
        "Return codes, assertions, or silent drop with counters on error?",
    ]
    if "irq" in prompt or "isr" in prompt or "interrupt" in title:
        bullets.append("Confirm ISR may only touch fields X; rest deferred to task.")

    seen: set[str] = set()
    unique: list[str] = []
    for b in bullets:
        if b not in seen:
            seen.add(b)
            unique.append(b)
    return unique[:6]


# ---------------------------------------------------------------------------
# Approach, data structures, edge cases, concurrency, tests
# ---------------------------------------------------------------------------

def approach_text(q: "Question") -> tuple[str, list[str]]:
    title = q.title
    cat = q.category
    intro = f"Build {title} in layers: define invariants first, implement the happy path, then harden edge cases and concurrency."

    plan = [
        "Restate API signatures and invariants aloud before writing code.",
        "Implement core logic with straightforward loops; optimize only after tests pass.",
        "Add minimal platform stubs (MMIO, IRQ save, monotonic timebase) so code compiles on host.",
        "Document ownership, error codes, and ISR vs task context in brief comments.",
    ]

    if cat == "rings_queues":
        plan.insert(1, "Choose spare-slot vs count field for occupancy; never mix models.")
    elif cat == "timers":
        plan.insert(1, "Store absolute deadlines; reprogram HW compare to earliest expiry on head change.")
    elif cat == "fsm":
        plan.insert(1, "Table- or switch-driven transitions; GENERIC_FAULT from every state.")
    elif cat == "drivers":
        plan.insert(1, "Separate HAL register access from policy (timeouts, retries, flow control).")
    elif cat == "protocol":
        plan.insert(1, "Single-pass parser with explicit return codes: need more data, OK, resync.")
    elif cat == "sync":
        plan.insert(1, "Pick lock-free only with proven algorithm; otherwise mutex/spinlock with clear rules.")
    elif cat == "dma":
        plan.insert(1, "Program descriptors; handle cache; IRQ only marks completion and kicks next chunk.")
    elif cat == "linux":
        plan.insert(1, "Follow kernel style: `devm_*` alloc, check all user copies, `-EINVAL`/`-EFAULT` paths.")
    elif cat == "cpp":
        plan.insert(1, "No heap/exceptions in ISR paths; prefer `constexpr`, RAII, and typed enums.")

    return intro, plan


def data_structures(q: "Question") -> list[str]:
    items = [
        "Structs/enums matching the prompt's Implement block — names unchanged for interviewer follow-up.",
        "Explicit capacity, generation counters, or state enum invariants in comments.",
        "Platform hooks (`regs`, `irq_save`, `now_ms`) isolated for unit test fakes.",
    ]
    t = q.title.lower()
    if "ring" in t or q.category == "rings_queues":
        items.append("Empty: `head==tail`; full: `next(head)==tail` (spare slot) unless count field used.")
    if q.category == "timers" or "timer" in t:
        items.append("Absolute expiry timestamps; wrap-safe compare via signed delta (`time_after`).")
    if q.category == "sync":
        items.append("Atomics with memory_order_acquire/release; IRQ-safe variants when needed.")
    if "heap" in t and "timer" in t:
        items.append("Min-heap indexed by `expires`; heap[0] is next IRQ deadline.")
    if "wheel" in t:
        items.append("Circular bucket array; cascade on tick for hierarchical wheels.")
    if q.category == "fsm":
        items.append("Current state + transition table rows indexed by `(state, event)`.")
    return items


def edge_cases(q: "Question") -> list[str]:
    cases = []
    t = q.title.lower()
    impl = q.implement.lower()

    if "null" in impl or "ptr" in impl or "*" in q.implement:
        cases.append("NULL pointer arguments — return error code, never dereference.")
    if "timeout" in t or "timeout" in impl:
        cases.append("Timeout expiry — return distinct error; leave hardware in bus-safe state.")
    if "ring" in impl or "queue" in t:
        cases.append("Push burst larger than free space — partial push or drop policy with counter.")
    if "full" in t or "capacity" in impl:
        cases.append("Capacity exhausted — return NULL/`-ENOMEM`/drop with stats.")
    if "wrap" in t or "time" in t:
        cases.append("Timestamp counter wrap — use signed delta compare; document max interval < 2³¹ ticks.")
    if "i2c" in impl or "spi" in impl:
        cases.append("NACK, arbitration loss, clock stretch timeout — recovery then error return.")
    if q.category == "fsm":
        cases.append("Invalid event in current state — remain in state or transition to FAULT per spec.")
    if "memmove" in t or "memcpy" in t or q.category == "memory_string":
        cases.append("Overlapping buffers — memmove direction; memcpy requires non-overlap.")
    if "cancel" in t:
        cases.append("Cancel while callback running — generation flag or cancel_sync handshake.")
    if "periodic" in t:
        cases.append("Re-arm during callback — avoid double-insert; use active/generation guard.")
    if "period" in impl and "sched" in t:
        cases.append("Sum of WCET exceeds period — feasibility check fails with clear return.")

    if not cases:
        cases = [
            "Zero-length operation — defined no-op success.",
            "Maximum size/at limit — correct result without overrun.",
            "Repeated calls idempotent where API semantics require it.",
        ]
    return cases[:6]


def concurrency_notes(q: "Question") -> str:
    cat = q.category
    prompt = q.prompt.lower()
    if cat == "linux":
        return (
            "Kernel: user copies via `copy_from_user`; sleeping only in process/thread context; "
            "spinlocks for short shared data; `devm_*` for probe-lifetime memory."
        )
    if cat == "cpp":
        return "No dynamic allocation in ISR; atomics with explicit orders; RAII for locks and DMA buffers."
    if cat in ("sync", "interrupts", "ipc", "rings_queues", "timers", "drivers", "dma", "logging"):
        return (
            "Label ISR-writable vs task-only fields. Use `irq_save`/`irq_restore` around "
            "list/timer mutations shared with ISR. Keep ISR < few µs; defer protocol parsing."
        )
    if "isr" in prompt or "irq" in prompt:
        return "ISR sets flags/enqueues only; task drains. If both touch state, IRQ-save critical section."
    return "N/A — single-threaded test harness; no ISR concurrency in scope."


def complexity_notes(q: "Question") -> list[str]:
    t = q.title.lower()
    if "heap" in t and "timer" in t:
        return [
            "| Operation | Time | Space |",
            "|---|---:|---:|",
            "| insert / cancel | O(log n) | O(n) heap |",
            "| pop expired | O(log n) amortized | O(1) extra |",
        ]
    if "wheel" in t:
        return [
            "| Operation | Time | Space |",
            "|---|---:|---:|",
            "| insert | O(1) | O(buckets + timers) |",
            "| tick | O(1) per slot + cascade | O(1) |",
        ]
    if "ring" in t or q.category == "rings_queues":
        return [
            "| Operation | Time | Space |",
            "|---|---:|---:|",
            "| push / pop | O(k) bytes moved | O(cap) buffer |",
            "| init | O(1) | O(1) |",
        ]
    if q.category == "protocol":
        return [
            "| Operation | Time | Notes |",
            "|---|---:|---|",
            "| per byte/frame | O(n) | single pass |",
            "| resync hunt | O(n) worst | bounded scan |",
        ]
    if q.category == "allocators":
        return [
            "| Operation | Time | Notes |",
            "|---|---:|---|",
            "| alloc / free | O(1) typical | pool/freelist |",
        ]
    if "sort" in t or "search" in t:
        return [
            "| Operation | Time | Space |",
            "|---|---:|---:|",
            "| primary | O(n log n) or O(n) | O(1) or O(n) |",
        ]
    return [
        "| Operation | Time | Space |",
        "|---|---:|---:|",
        "| primary API | O(1) typical | O(1) or O(cap) struct |",
        "| init | O(cap) or O(1) | O(cap) if buffer |",
    ]


def test_cases(q: "Question") -> tuple[list[str], str]:
    cases = [
        "Happy path — minimal valid input produces expected output/state.",
        "Zero/null/empty input — defined no-op or error code, no crash.",
        "Boundary — max capacity, max timeout, wrap boundary minus one.",
        "Stress — back-to-back calls, burst traffic, re-entrancy where applicable.",
    ]
    t = q.title.lower()
    if q.category == "fsm":
        cases.append("Invalid event in each state; GENERIC_FAULT from every state reaches FAULT.")
    if "ring" in t:
        cases.append("Fill exactly to full then push one — reject or drop per policy.")
    if "timer" in t:
        cases.append("Two timers — earlier fires first; cancel head reprograms HW.")
    if "cancel" in t:
        cases.append("Cancel from task while callback runs — no double-free or use-after-free.")
    if "memmove" in t:
        cases.append("Overlapping regions forward and backward.")

    lang = "cpp" if q.lang == "cpp" else "c"
    test_code = f"""#ifdef TEST_{q.id}
#include <assert.h>

int main(void) {{
    /* TODO: wire to {q.id} APIs from Step 3 */
    assert(1); /* replace with real checks */
    return 0;
}}
#endif"""
    return cases, test_code


# ---------------------------------------------------------------------------
# Expanded implementations for common stub patterns (by question id)
# ---------------------------------------------------------------------------

EXPANDED_STUB_CODE: dict[str, str] = {
    "C173": r"""#include <stdint.h>
#include <stddef.h>

typedef void (*timer_cb)(void *ctx);

typedef struct sw_timer {
    struct sw_timer *next;
    uint32_t expires_ms;
    timer_cb cb;
    void *ctx;
    uint8_t active;
} sw_timer_t;

static sw_timer_t *g_head;
static uint32_t g_now_ms;

#define time_before(a, b)    ((int32_t)((a) - (b)) < 0)
#define time_before_eq(a, b) ((int32_t)((a) - (b)) <= 0)

static uint32_t irq_save(void) { return 0; }
static void irq_restore(uint32_t f) { (void)f; }

static void hw_timer_program(uint32_t deadline_ms) {
    uint32_t delta = deadline_ms - g_now_ms;
    (void)delta; /* platform: write compare register */
}

static void reprogram_hw(void) {
    if (g_head) {
        hw_timer_program(g_head->expires_ms);
    }
}

static void list_remove(sw_timer_t *t) {
    sw_timer_t **pp = &g_head;
    while (*pp) {
        if (*pp == t) {
            *pp = t->next;
            return;
        }
        pp = &(*pp)->next;
    }
}

static void insert_sorted(sw_timer_t *t) {
    t->next = NULL;
    if (!g_head || time_before(t->expires_ms, g_head->expires_ms)) {
        t->next = g_head;
        g_head = t;
        reprogram_hw();
        return;
    }
    sw_timer_t *p = g_head;
    while (p->next && time_before_eq(p->next->expires_ms, t->expires_ms)) {
        p = p->next;
    }
    t->next = p->next;
    p->next = t;
}

void sw_timer_cancel(sw_timer_t *t) {
    uint32_t flags = irq_save();
    t->active = 0;
    if (g_head == t) {
        g_head = t->next;
        reprogram_hw();
    } else {
        list_remove(t);
    }
    irq_restore(flags);
}

void sw_timer_set(sw_timer_t *t, uint32_t delay_ms, timer_cb cb, void *ctx) {
    uint32_t flags = irq_save();
    if (t->active) {
        sw_timer_cancel(t);
    }
    t->expires_ms = g_now_ms + delay_ms;
    t->cb = cb;
    t->ctx = ctx;
    t->active = 1;
    insert_sorted(t);
    irq_restore(flags);
}

void hw_timer_irq(void) {
    /* Called when HW compare fires; advance time to programmed deadline or read HW */
    if (g_head) {
        g_now_ms = g_head->expires_ms;
    }
    while (g_head && time_before_eq(g_head->expires_ms, g_now_ms)) {
        sw_timer_t *exp = g_head;
        g_head = exp->next;
        exp->active = 0;
        if (exp->cb) {
            exp->cb(exp->ctx);
        }
    }
    reprogram_hw();
}

void tick_ms(uint32_t ms) { g_now_ms = ms; }""",
    "C174": r"""#include <stdint.h>
#include <stddef.h>

typedef void (*timer_cb)(void *ctx);

typedef struct sw_timer {
    struct sw_timer *next;
    uint32_t expires_ms;
    uint32_t period_ms;
    timer_cb cb;
    void *ctx;
    uint8_t active;
    uint8_t periodic;
    uint8_t in_callback;
    uint32_t generation;
} sw_timer_t;

static sw_timer_t *g_head;
static uint32_t g_now_ms;

#define time_before_eq(a, b) ((int32_t)((a) - (b)) <= 0)

static uint32_t irq_save(void) { return 0; }
static void irq_restore(uint32_t f) { (void)f; }

static void reprogram_hw(void) { (void)g_head; }

static void insert_sorted(sw_timer_t *t);
static void list_remove(sw_timer_t *t);

void sw_timer_cancel(sw_timer_t *t) {
    uint32_t f = irq_save();
    t->active = 0;
    list_remove(t);
    irq_restore(f);
}

void sw_timer_set_periodic(sw_timer_t *t, uint32_t period_ms, timer_cb cb, void *ctx) {
    uint32_t f = irq_save();
    if (t->active) {
        list_remove(t);
    }
    t->period_ms = period_ms;
    t->cb = cb;
    t->ctx = ctx;
    t->periodic = 1;
    t->active = 1;
    t->expires_ms = g_now_ms + period_ms;
    insert_sorted(t);
    irq_restore(f);
}

static void fire_timer(sw_timer_t *exp) {
    exp->in_callback = 1;
    uint32_t gen = exp->generation;
    if (exp->cb) {
        exp->cb(exp->ctx);
    }
    exp->in_callback = 0;
    if (!exp->active || exp->generation != gen) {
        return;
    }
    if (exp->periodic) {
        exp->expires_ms += exp->period_ms;
        insert_sorted(exp);
    }
}

int sw_timer_cancel_sync(sw_timer_t *t) {
    sw_timer_cancel(t);
    while (t->in_callback) {
        /* yield or wfe in real RTOS */
    }
    return 0;
}

static void insert_sorted(sw_timer_t *t) {
    t->next = NULL;
    sw_timer_t **pp = &g_head;
    while (*pp && time_before_eq((*pp)->expires_ms, t->expires_ms)) {
        pp = &(*pp)->next;
    }
    t->next = *pp;
    *pp = t;
    reprogram_hw();
}

static void list_remove(sw_timer_t *t) {
    sw_timer_t **pp = &g_head;
    while (*pp) {
        if (*pp == t) {
            *pp = t->next;
            t->generation++;
            reprogram_hw();
            return;
        }
        pp = &(*pp)->next;
    }
}""",
    "C175": r"""#include <stdint.h>
#include <stddef.h>

/* Max representable interval: half the counter space (2^31 ticks for 32-bit) */
#define TIME_MAX_DELTA_MS 0x7FFFFFFFu

int time_after(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) > 0;
}

int time_before(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) < 0;
}

int time_before_eq(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) <= 0;
}

uint32_t time_delta(uint32_t now, uint32_t then) {
    return now - then;
}

int time_in_range(uint32_t t, uint32_t start, uint32_t end) {
    return time_after(t, start) && time_before_eq(t, end);
}""",
    "C176": r"""#include <stdint.h>
#include <stddef.h>

typedef void (*timer_cb)(void *ctx);

typedef struct sw_timer {
    struct sw_timer *next;
    timer_cb cb;
    void *ctx;
    uint32_t expires_tick;
} sw_timer_t;

#define WHEEL_SLOTS 256u
#define WHEEL_MASK  (WHEEL_SLOTS - 1u)

typedef struct {
    sw_timer_t *buckets[WHEEL_SLOTS];
    uint32_t cursor;
    uint32_t tick;
} wheel_t;

static void wheel_insert(wheel_t *w, sw_timer_t *t, uint32_t expires_tick) {
    uint32_t slot = expires_tick & WHEEL_MASK;
    t->expires_tick = expires_tick;
    t->next = w->buckets[slot];
    w->buckets[slot] = t;
}

static void wheel_tick(wheel_t *w) {
    uint32_t slot = w->tick & WHEEL_MASK;
    sw_timer_t *t = w->buckets[slot];
    w->buckets[slot] = NULL;
    while (t) {
        sw_timer_t *n = t->next;
        if (t->cb) {
            t->cb(t->ctx);
        }
        t = n;
    }
    w->tick++;
    w->cursor = slot;
}""",
    "C177": r"""#include <stdint.h>
#include <stddef.h>

typedef struct sw_timer {
    uint32_t expires;
    int index;
} sw_timer_t;

typedef struct {
    sw_timer_t **heap;
    size_t n;
    size_t cap;
} heap_t;

static int time_before_eq(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) <= 0;
}

static void heap_swap(heap_t *h, size_t i, size_t j) {
    sw_timer_t *tmp = h->heap[i];
    h->heap[i] = h->heap[j];
    h->heap[j] = tmp;
    h->heap[i]->index = (int)i;
    h->heap[j]->index = (int)j;
}

static void heap_up(heap_t *h, size_t i) {
    while (i > 0) {
        size_t p = (i - 1) / 2;
        if (time_before_eq(h->heap[i]->expires, h->heap[p]->expires)) {
            heap_swap(h, i, p);
            i = p;
        } else {
            break;
        }
    }
}

static void heap_down(heap_t *h, size_t i) {
    for (;;) {
        size_t l = 2 * i + 1, r = l + 1, m = i;
        if (l < h->n && time_before_eq(h->heap[l]->expires, h->heap[m]->expires)) {
            m = l;
        }
        if (r < h->n && time_before_eq(h->heap[r]->expires, h->heap[m]->expires)) {
            m = r;
        }
        if (m == i) {
            break;
        }
        heap_swap(h, i, m);
        i = m;
    }
}

void heap_timer_insert(heap_t *h, sw_timer_t *t) {
    if (h->n >= h->cap) {
        return;
    }
    h->heap[h->n] = t;
    t->index = (int)h->n;
    h->n++;
    heap_up(h, h->n - 1);
}

sw_timer_t *heap_timer_pop_expired(heap_t *h, uint32_t now) {
    if (!h->n || !time_before_eq(h->heap[0]->expires, now)) {
        return NULL;
    }
    sw_timer_t *top = h->heap[0];
    h->n--;
    if (h->n) {
        h->heap[0] = h->heap[h->n];
        h->heap[0]->index = 0;
        heap_down(h, 0);
    }
    return top;
}""",
    "C178": r"""#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t anchor;
    uint32_t next;
    uint32_t period;
    uint32_t missed;
} periodic_t;

void periodic_arm(periodic_t *p, uint32_t now, uint32_t period) {
    p->anchor = now;
    p->period = period;
    p->next = now + period;
    p->missed = 0;
}

void periodic_on_fire(periodic_t *p, uint32_t now) {
    p->next += p->period;
    if ((int32_t)(now - p->next) > 0) {
        uint32_t late = now - p->next;
        p->missed += late / p->period + 1;
        p->next = now + p->period;
    }
}""",
    "C179": r"""#include <stdint.h>
#include <stddef.h>

typedef void (*task_fn)(void);

typedef struct {
    task_fn fn;
    const char *name;
} task_t;

static task_t g_tasks[8];
static int g_count;
static int g_current;

void task_add(task_fn fn, const char *name) {
    if (g_count < 8) {
        g_tasks[g_count].fn = fn;
        g_tasks[g_count].name = name;
        g_count++;
    }
}

void scheduler_run(void) {
    if (g_count == 0) {
        return;
    }
    g_tasks[g_current].fn();
    g_current = (g_current + 1) % g_count;
}""",
    "C180": r"""#include <stdint.h>
#include <stddef.h>

#define MAX_PRIO 8

typedef void (*task_fn)(void);

typedef struct {
    task_fn fn;
    uint8_t ready;
} task_slot_t;

typedef struct {
    task_slot_t queues[MAX_PRIO][4];
    uint8_t qcount[MAX_PRIO];
    uint8_t ready_bitmap;
} ready_queue_t;

static int clz8(uint8_t x) {
    if (!x) return 8;
    int n = 0;
    while (!(x & 0x80u)) { x <<= 1; n++; }
    return n;
}

void rq_add(ready_queue_t *rq, int prio, task_fn fn) {
    if (prio < 0 || prio >= MAX_PRIO) return;
    if (rq->qcount[prio] >= 4) return;
    int i = rq->qcount[prio]++;
    rq->queues[prio][i].fn = fn;
    rq->queues[prio][i].ready = 1;
    rq->ready_bitmap |= (uint8_t)(1u << prio);
}

task_fn rq_pick_next(ready_queue_t *rq) {
    if (!rq->ready_bitmap) return NULL;
    int p = 7 - clz8(rq->ready_bitmap);
    for (int i = 0; i < rq->qcount[p]; ++i) {
        if (rq->queues[p][i].ready) {
            rq->queues[p][i].ready = 0;
            return rq->queues[p][i].fn;
        }
    }
    return NULL;
}""",
    "C181": r"""#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t deadline;
    int (*fn)(void);
    uint8_t active;
} deadline_t;

static int time_after(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) > 0;
}

int run_deadlines(deadline_t *d, size_t n, uint32_t now) {
    int ran = 0;
    for (size_t i = 0; i < n; ++i) {
        if (d[i].active && time_after(now, d[i].deadline)) {
            d[i].fn();
            d[i].active = 0;
            ran++;
        }
    }
    return ran;
}

void reg_call(deadline_t *d, uint32_t deadline_ms, int (*fn)(void)) {
    d->deadline = deadline_ms;
    d->fn = fn;
    d->active = 1;
}""",
    "C182": r"""#include <stdint.h>
#include <stddef.h>

typedef struct {
    uint32_t wcet_us;
    uint32_t period_us;
    uint32_t miss_count;
} task_profile_t;

int sched_feasibility(task_profile_t *t, size_t n, uint32_t frame_us) {
    uint64_t sum = 0;
    for (size_t i = 0; i < n; ++i) {
        sum += t[i].wcet_us;
    }
    return sum <= frame_us ? 0 : -1;
}

void on_deadline_miss(task_profile_t *t) {
    t->miss_count++;
}""",
    "C183": r"""#include <stdint.h>
#include <stddef.h>

typedef struct timer_node {
    struct timer_node *next;
    uint32_t abs_expires;
} timer_node_t;

#define TVR_BITS 8
#define TVN_BITS 6
#define TVR_SIZE (1u << TVR_BITS)

typedef struct {
    timer_node_t *vec[TVR_SIZE];
    uint32_t jiffies;
} tvec_base_t;

static uint32_t timer_jiffies(tvec_base_t *base) {
    return base->jiffies;
}

void wheel_cascade(tvec_base_t *base, unsigned idx) {
    (void)base;
    (void)idx;
}

void tickless_sleep_until(uint32_t target_jiffies) {
    uint32_t now = 0; /* read monotonic tick */
    if ((int32_t)(target_jiffies - now) <= 0) {
        return;
    }
    /* program HW one-shot for (target - now) */
}""",
    "C184": r"""#include <stdint.h>
#include <stddef.h>

typedef void (*debounce_cb)(int level, void *ctx);

typedef struct {
    uint32_t delay_ms;
    debounce_cb cb;
    void *ctx;
    uint8_t pending_level;
    uint8_t armed;
} debounce_t;

static uint32_t g_now;

extern void sw_timer_set(void *t, uint32_t ms, void (*cb)(void*), void *ctx);
extern void sw_timer_cancel(void *t);

static void debounce_fire(void *ctx) {
    debounce_t *d = (debounce_t *)ctx;
    d->armed = 0;
    if (d->cb) {
        d->cb((int)d->pending_level, d->ctx);
    }
}

void debounce_on_edge(debounce_t *d, int level) {
    d->pending_level = (uint8_t)level;
    sw_timer_cancel(&d->armed);
    sw_timer_set(&d->armed, d->delay_ms, debounce_fire, d);
}""",
    "C139": r"""#include <stdint.h>
#include <stddef.h>

typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
} uart_t;

#define UART_TXE  (1u << 7)
#define UART_TC   (1u << 6)

extern size_t uart_tx_ring_pending(void);

int uart_flush(uint32_t timeout_ms) {
    uart_t *u = (uart_t *)0x40000000u; /* platform base */
    while (uart_tx_ring_pending() > 0) {
        if (timeout_ms == 0) {
            return -1;
        }
        timeout_ms--;
    }
    while (!(u->SR & UART_TC)) {
        if (timeout_ms == 0) {
            return -2;
        }
        timeout_ms--;
    }
    return 0;
}""",
    "C185": r"""#include <stdint.h>
#include <stddef.h>

typedef enum { TIMER_ONESHOT, TIMER_PERIODIC } timer_mode_t;

typedef struct {
    volatile uint32_t CR;
    volatile uint32_t ARR;
    volatile uint32_t CNT;
} hw_timer_t;

#define CR_EN   (1u << 0)
#define CR_OPM  (1u << 1)

void hal_timer_start(hw_timer_t *t, uint32_t ticks, timer_mode_t mode) {
    t->ARR = ticks;
    t->CNT = 0;
    t->CR = CR_EN | (mode == TIMER_ONESHOT ? CR_OPM : 0);
}

void hal_timer_stop(hw_timer_t *t) {
    t->CR = 0;
}

int timer_self_test(void) {
    return time_before_eq(5u, 10u) ? 0 : -1;
}

static int time_before_eq(uint32_t a, uint32_t b) {
    return (int32_t)(a - b) <= 0;
}""",
}


def finalize_code(q: "Question", code: str) -> str:
    """Pick best code variant and format for interview readability."""
    if q.id in EXPANDED_STUB_CODE:
        code = EXPANDED_STUB_CODE[q.id]
    elif is_stub_code(code) and q.implement.strip() not in ("/* see prompt */", ""):
        code = q.implement
    return beautify_c_code(code)
