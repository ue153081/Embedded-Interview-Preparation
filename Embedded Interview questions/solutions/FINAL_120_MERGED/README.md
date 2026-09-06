# FINAL 120 — Merged Topic Solutions

**Question list:** [`../../FINAL_120_MERGED_TOPICS.md`](../../FINAL_120_MERGED_TOPICS.md)  
**40 prep topics** (M001–M044) — one comprehensive solution per merged topic.  
*(M045 is mock checkpoint only — no solution file.)*

Regenerate: `python3 tools/generate_merged_solutions.py`

## All solutions

| ID | Topic | Type | Original Qs | File |
|----|-------|------|-------------|------|
| M001 | Memory byte operations (memcpy / memmove | Coding | Q001, Q002 | [M001_memory_byte_ops.md](./M001_memory_byte_ops.md) |
| M002 | Safe string / integer parsing | Coding | Q003 | [M002_safe_atoi.md](./M002_safe_atoi.md) |
| M003 | Endianness, wire layout & struct unpacki | Coding | Q004, Q010, Q014 | [M003_endian_wire_struct.md](./M003_endian_wire_struct.md) |
| M004 | Bit manipulation toolkit | Coding | Q005, Q006, Q007, Q008, Q009, Q013 | [M004_bit_manipulation.md](./M004_bit_manipulation.md) |
| M005 | CRC & checksums | Coding | Q011, Q012 | [M005_crc_checksums.md](./M005_crc_checksums.md) |
| M006 | Ring buffers & SPSC queues (complete) | Coding | Q016, Q017, Q018, Q019, Q020, Q021 | [M006_ring_buffers_SPSC_complete.md](./M006_ring_buffers_SPSC_complete.md) |
| M007 | IPC, mailboxes & lock-free handoff | Coding | Q022, Q023, Q024, Q025, Q026, Q027, Q028 | [M007_ipc_mailboxes.md](./M007_ipc_mailboxes.md) |
| M008 | Memory allocators (pools → heap → specia | Coding | Q029, Q030, Q031, Q032, Q033, Q034, Q035, Q036 | [M008_memory_allocators.md](./M008_memory_allocators.md) |
| M009 | Locks, semaphores & reader–writer | Coding | Q037, Q038, Q039, Q040, Q041 | [M009_locks_semaphores_rw.md](./M009_locks_semaphores_rw.md) |
| M010 | Atomics, memory order & cache effects | Coding | Q042, Q043, Q044, Q045 | [M010_atomics_memory_order.md](./M010_atomics_memory_order.md) |
| M011 | MMIO register HAL & timed polling | Coding | Q046, Q047 | [M011_mmio_hal_polling.md](./M011_mmio_hal_polling.md) |
| M012 | UART driver (poll → IRQ → DMA) | Coding | Q048, Q049, Q050 | [M012_uart_driver_stack.md](./M012_uart_driver_stack.md) |
| M013 | SPI driver (blocking → IRQ/DMA) | Coding | Q051, Q052 | [M013_spi_driver.md](./M013_spi_driver.md) |
| M014 | I2C master (transfer + recovery) | Coding | Q053, Q054 | [M014_i2c_master_recovery.md](./M014_i2c_master_recovery.md) |
| M015 | GPIO, debounce, PWM, ADC & sensor wrappe | Coding | Q055, Q056, Q057, Q058 | [M015_gpio_debounce_pwm_adc.md](./M015_gpio_debounce_pwm_adc.md) |
| M016 | Watchdog & deadline monitoring | Coding | Q059, Q065 | [M016_watchdog_deadline.md](./M016_watchdog_deadline.md) |
| M017 | Protocol stream parser (framing + CRC +  | Coding | Q060 | [M017_protocol_parser.md](./M017_protocol_parser.md) |
| M018 | Software timers & tick dispatch | Coding | Q061, Q062, Q063, Q064 | [M018_software_timers.md](./M018_software_timers.md) |
| M019 | Reliability patterns (backoff, fault FSM | Coding | Q066, Q067 | [M019_reliability_backoff_fsm.md](./M019_reliability_backoff_fsm.md) |
| M020 | Classic FSM coding | Coding | Q068 | [M020_classic_fsm.md](./M020_classic_fsm.md) |
| M021 | Filters & signal-lite numeric | Coding | Q069 | [M021_filters_ewma.md](./M021_filters_ewma.md) |
| M022 | Embedded unit-test harness | Coding | Q070 | [M022_unit_test_harness.md](./M022_unit_test_harness.md) |
| M023 | C macros & intrusive structures | Coding | Q015 | [M023_macros_intrusive_list.md](./M023_macros_intrusive_list.md) |
| M026 | Memory model: volatile, atomics, barrier | Verbal | Q071, Q078, Q083, Q084 | [M026_memory_model_verbal.md](./M026_memory_model_verbal.md) |
| M027 | Interrupt architecture (ISR rules, defer | Verbal | Q072, Q073, Q095 | [M027_interrupt_architecture.md](./M027_interrupt_architecture.md) |
| M028 | Synchronization choice & failure modes | Verbal | Q074, Q075, Q076, Q089 | [M028_sync_choice_failure.md](./M028_sync_choice_failure.md) |
| M029 | DMA, cache & ARM ordering instructions | Verbal | Q077, Q079 | [M029_dma_cache_ordering.md](./M029_dma_cache_ordering.md) |
| M030 | Runtime environments & memory layout | Verbal | Q080, Q082 | [M030_runtime_memory_layout.md](./M030_runtime_memory_layout.md) |
| M031 | Boot, MMU, MPU & TrustZone | Verbal | Q081, Q085, Q099 | [M031_boot_mmu_trustzone.md](./M031_boot_mmu_trustzone.md) |
| M032 | Measurement, debug & heisenbugs | Verbal | Q086, Q087, Q088 | [M032_measurement_debug.md](./M032_measurement_debug.md) |
| M033 | Buses & protocols (I2C, CAN, endian) | Verbal | Q090, Q091, Q092 | [M033_buses_protocols_verbal.md](./M033_buses_protocols_verbal.md) |
| M034 | Linux driver interface & platform model | Verbal | Q093, Q094, Q096 | [M034_linux_driver_platform.md](./M034_linux_driver_platform.md) |
| M035 | Security & safety concepts | Verbal | Q097, Q098 | [M035_security_safety.md](./M035_security_safety.md) |
| M036 | RT validation & system-level verbal | Verbal | Q100 | [M036_rt_validation_system.md](./M036_rt_validation_system.md) |
| M039 | Driver stacks & bus frameworks | Design | Q101, Q106, Q107 | [M039_driver_stacks_frameworks.md](./M039_driver_stacks_frameworks.md) |
| M040 | Data path: ISR → task → DMA → pipeline | Design | Q102, Q105, Q116, Q117 | [M040_data_path_pipeline.md](./M040_data_path_pipeline.md) |
| M041 | Platform services: timers, logging, watc | Design | Q103, Q104, Q108, Q109 | [M041_platform_services.md](./M041_platform_services.md) |
| M042 | Boot, OTA, security & power | Design | Q110, Q111, Q118, Q119 | [M042_boot_ota_security_power.md](./M042_boot_ota_security_power.md) |
| M043 | Multi-core, encoder & gateway systems | Design | Q112, Q113, Q114, Q115 | [M043_multicore_encoder_gateway.md](./M043_multicore_encoder_gateway.md) |
| M044 | Test, bring-up & validation architecture | Design | Q120 | [M044_test_bringup_validation.md](./M044_test_bringup_validation.md) |

**Total: 40 solution files**
