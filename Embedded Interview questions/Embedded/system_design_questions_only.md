# Embedded System Design — Questions Only Sheet

1. Design a UART driver stack that supports polling, interrupt, and DMA modes behind one public API.
2. Design an ISR-to-task event pipeline with bounded latency and explicit backpressure behavior.
3. Design a firmware logging subsystem with ring buffering, log levels, and crash-safe persistence strategy.
4. Design a software timer service and justify sorted list vs min-heap vs timer wheel.
5. Design a priority-based scheduler queue with fairness and starvation prevention.
6. Design an embedded memory manager combining fixed pools and variable-size allocation with diagnostics.
7. Design a DMA framework with descriptor ownership states, completion handling, and error recovery.
8. Design a register HAL abstraction that is portable across MCU families and unit-test friendly.
9. Design an I2C transaction engine with retries, timeouts, and stuck-bus recovery.
10. Design an SPI transfer framework supporting blocking, interrupt-driven, and DMA paths.
11. Design a system watchdog architecture using task heartbeats and controlled reset policy.
12. Design a fault-management framework with error classification, retry policy, and degrade/reset actions.
13. Design driver power-management support for suspend/resume with context preservation.
14. Design a dual-core mailbox IPC layer using shared memory and interrupt notifications.
15. Design an OTA update system using A/B slots, integrity checks, and rollback logic.
16. Design a complete boot flow from reset vector to application handoff with failure handling.
17. Design a telemetry pipeline with batching, retry/jitter, and bounded memory usage.
18. Design a streaming packet parser framework with framing, CRC validation, and resynchronization.
19. Design a real-time sensor processing pipeline from DMA capture to filtered outputs and alerts.
20. Design a driver test architecture with fake registers, fault injection, and timing validation.
21. Design an interrupt-controller abstraction with dynamic handler registration and prioritization.
22. Design a cache-coherency boundary API for CPU, DMA, and multi-core shared buffers.
23. Design a secure firmware loading pipeline with authentication and anti-rollback protections.
24. Design a crash dump system defining capture scope, storage strategy, and post-reset retrieval.
25. Design a platform initialization sequence covering clocks, memory, peripheral bring-up, and health checks.
