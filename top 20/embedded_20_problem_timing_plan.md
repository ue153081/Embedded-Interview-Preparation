# Embedded Interview Coding Practice Plan (20 Problems)

This document provides **target completion times** for implementing each
problem during practice. The goal is to simulate a **45‑minute embedded
screening interview**, where you must code quickly and leave time for
explanation and follow‑ups.

Recommended timing guideline:

-   Easy problems: **5--6 minutes**
-   Medium problems: **8--10 minutes**
-   Hard problems: **12--15 minutes**

------------------------------------------------------------------------

# Low‑Level C Fundamentals

  \#   Problem                                                    Target Time
  ---- ---------------------------------------------------------- -------------
  1    Implement `memcpy`                                         5 min
  2    Implement `memmove`                                        6 min
  3    Bit manipulation utilities (set/clear/toggle/count bits)   5 min

Why these matter: - Test pointer arithmetic - Show understanding of
memory operations - Demonstrate register manipulation skills

------------------------------------------------------------------------

# Buffer and Queue Data Structures

  \#   Problem                        Target Time
  ---- ------------------------------ -------------
  4    Circular buffer library        8--10 min
  5    Lock‑free ring buffer (SPSC)   10--12 min
  6    Interrupt‑safe queue           8--10 min

Important aspects to handle:

-   Buffer full condition
-   Buffer empty condition
-   Wraparound logic
-   ISR vs application interaction

------------------------------------------------------------------------

# Memory Management

  \#   Problem                       Target Time
  ---- ----------------------------- -------------
  7    Fixed memory pool allocator   10--12 min
  8    Free‑list heap allocator      12--15 min

Concepts tested:

-   Pointer manipulation
-   Deterministic allocation
-   Fragmentation management

------------------------------------------------------------------------

# Embedded System Patterns

  \#   Problem                                  Target Time
  ---- ---------------------------------------- -------------
  9    State machine implementation             6--8 min
  10   Event queue system                       8--10 min
  11   Logging subsystem (ring buffer logger)   10 min

Why interviewers ask these:

-   Demonstrates event‑driven architecture
-   Shows modular firmware design
-   Tests real firmware patterns

------------------------------------------------------------------------

# Driver Architecture

  \#   Problem                          Target Time
  ---- -------------------------------- -------------
  12   UART interrupt driver skeleton   12--15 min
  13   UART DMA driver skeleton         12--15 min
  14   SPI driver skeleton              8--10 min
  15   I2C driver skeleton              8--10 min

Expected in interviews:

-   Register structure usage
-   Interrupt handling
-   Buffer management

------------------------------------------------------------------------

# Timer Systems

  \#   Problem                    Target Time
  ---- -------------------------- -------------
  16   Software timer scheduler   10--12 min
  17   Timer callback scheduler   10--12 min

Concepts tested:

-   periodic timers
-   one‑shot timers
-   tick‑based scheduling

------------------------------------------------------------------------

# High‑Performance Streaming

  \#   Problem                       Target Time
  ---- ----------------------------- -------------
  18   DMA double‑buffer streaming   8--10 min

Why important:

-   Used in audio/video streaming
-   Common in high‑speed peripherals

------------------------------------------------------------------------

# Protocol Processing

  \#   Problem                              Target Time
  ---- ------------------------------------ -------------
  19   UART packet parser (state machine)   10--12 min

Typical frame format:

START → LENGTH → DATA → CRC

------------------------------------------------------------------------

# System Abstraction

  \#   Problem                    Target Time
  ---- -------------------------- -------------
  20   Generic driver framework   8--10 min

Concepts:

-   device abstraction
-   driver operations tables
-   hardware independence

------------------------------------------------------------------------

# Ideal Practice Strategy

Practice solving **4--5 problems per session**.

Example session:

-   memcpy --- 5 min\
-   circular buffer --- 10 min\
-   memory pool allocator --- 12 min\
-   state machine --- 6 min\
-   event queue --- 8 min

Total: \~40 minutes

This closely simulates the **actual interview environment**.

------------------------------------------------------------------------

# Final Goal

You should be able to implement:

-   Easy problems in **≤6 minutes**
-   Medium problems in **≤10 minutes**
-   Hard problems in **≤15 minutes**

Achieving these timings will give you enough time in a real interview
for:

-   explaining design decisions
-   handling edge cases
-   answering follow‑up questions
