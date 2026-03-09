# Top 25 Embedded System Design Interview Questions

This document lists **25 high-frequency embedded system design
questions** commonly discussed in embedded firmware interviews at
companies such as **ARM, Qualcomm, NVIDIA, Apple, Google, and Tesla**.

The goal of this list is **depth over breadth**. If you can confidently
explain these designs with architecture diagrams, trade-offs, and
implementation approaches, you will be well-prepared for most embedded
system design interviews.

------------------------------------------------------------------------

# 1. Driver Design

1.  Design an **interrupt-driven UART driver** using TX/RX ring buffers.
2.  Design a **DMA-based UART driver** for high-speed communication.
3.  Design a **SPI driver supporting multiple devices** on the same bus.
4.  Design an **I2C driver supporting multiple slaves** with
    arbitration.
5.  Design a **GPIO driver supporting interrupt callbacks**.

------------------------------------------------------------------------

# 2. Interrupt and Event Systems

6.  Design an **event-driven firmware architecture**.
7.  Design an **event queue for ISR → main loop communication**.
8.  Design a **message queue shared between ISR and tasks**.
9.  Design a **deferred interrupt processing system**.

------------------------------------------------------------------------

# 3. Timer and Scheduling Systems

10. Design a **software timer scheduler**.
11. Design a **bare-metal task scheduler**.
12. Design a **priority-based task scheduler**.

------------------------------------------------------------------------

# 4. Memory Management

13. Design a **fixed-size memory pool allocator**.
14. Design a **variable-size free-list allocator**.
15. Design a **memory management strategy that avoids fragmentation**.

------------------------------------------------------------------------

# 5. High-Speed Data Systems

16. Design a **DMA-based data acquisition system**.
17. Design a **circular DMA buffer system**.
18. Design a **double-buffered data processing pipeline**.

------------------------------------------------------------------------

# 6. Communication Systems

19. Design a **packet-based communication protocol**.
20. Design a **robust serial protocol with error detection and
    retransmission**.

------------------------------------------------------------------------

# 7. Firmware Architecture

21. Design a **hardware abstraction layer (HAL)**.
22. Design a **modular embedded firmware architecture**.

------------------------------------------------------------------------

# 8. Reliability and Debugging

23. Design an **embedded logging system**.
24. Design a **watchdog-based fault recovery system**.

------------------------------------------------------------------------

# 9. Firmware Update Systems

25. Design a **bootloader supporting firmware updates**.

------------------------------------------------------------------------

# How to Use This List for Interview Preparation

Focus on the following while preparing each design:

-   Architecture diagram
-   Core data structures
-   Interrupt handling strategy
-   Memory usage strategy
-   Error handling
-   Scalability considerations

------------------------------------------------------------------------

# Suggested Preparation Order

For most embedded firmware interviews, start with these topics:

1.  Interrupt-driven UART driver
2.  Event queue system
3.  Software timer scheduler
4.  Memory pool allocator
5.  Free-list allocator
6.  DMA-based data pipeline
7.  Embedded logging system
8.  Bootloader design

Mastering these will cover **a large portion of embedded system design
discussions in interviews**.
