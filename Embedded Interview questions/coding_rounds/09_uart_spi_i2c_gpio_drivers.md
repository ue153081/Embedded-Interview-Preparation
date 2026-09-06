# UART / SPI / I2C / GPIO Drivers

**IDs:** C136–C160 (25 questions)  
**Focus:** Polling and IRQ drivers, bus recovery, debounce, multi-instance.

[← Back to category index](./README.md)

---

### C136 — UART polling TX/RX

**Interview prompt:**  
Implement blocking UART transmit/receive by polling status registers (fake MMIO OK).

**Implement:**
```c
int uart_putc(char c);
int uart_getc(uint32_t timeout_ms);
int uart_write(const char *s, size_t n);
```

**Constraints / expectations:**
- Timeout on RX
- Check TX empty / RX ready bits

**Follow-ups:**
- Error flags framing/overrun
- Non-blocking API

---

### C137 — UART IRQ RX to ring

**Interview prompt:**  
IRQ on RX pushes bytes into a ring buffer consumed by a task.

**Implement:**
```c
void uart_rx_isr(void);
size_t uart_read(uint8_t *dst, size_t n);
```

**Constraints / expectations:**
- ISR short
- Drop policy on full

**Follow-ups:**
- High-water callback
- DMA later

---

### C138 — UART IRQ TX from ring

**Interview prompt:**  
Kickstart TX interrupt; ISR pulls from ring until empty then disables TX IRQ.

**Implement:**
```c
int uart_write_irq(const uint8_t *src, size_t n);
void uart_tx_isr(void);
```

**Constraints / expectations:**
- Enable TX IRQ only when needed
- No busy wait in write if async—document

**Follow-ups:**
- TX complete callback
- Half-duplex RS485 DE pin

---

### C139 — UART drain / flush

**Interview prompt:**  
Wait until TX ring+shift register drained.

**Implement:**
```c
int uart_flush(uint32_t timeout_ms);
```

**Constraints / expectations:**
- Timeout
- ISR interaction

**Follow-ups:**
- flush vs power-off
- Break signal

---

### C140 — Software RTS/CTS

**Interview prompt:**  
Implement SW flow control: stop accepting RX when local ring high; drive RTS; honor CTS before TX.

**Implement:**
```c
void uart_flow_on_rx_wm(void);
int uart_write_with_cts(const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Watermarks
- Document pin polarity

**Follow-ups:**
- HW flow control regs
- Deadlock if both sides stuck

---

### C141 — UART error recovery

**Interview prompt:**  
Count framing/overrun/parity errors in ISR and recover receiver.

**Implement:**
```c
void uart_err_isr(void);
typedef struct { uint32_t overrun, framing, parity; } uart_err_t;
```

**Constraints / expectations:**
- Read status correctly (order)
- Clear sticky errors

**Follow-ups:**
- When to reset RX FIFO
- User-visible stats

---

### C142 — SPI polling transfer

**Interview prompt:**  
Full-duplex SPI transfer of n bytes polling TX/RX flags.

**Implement:**
```c
int spi_transfer(const uint8_t *tx, uint8_t *rx, size_t n);
```

**Constraints / expectations:**
- Handle tx or rx NULL as discard/dummy
- CS control outside or inside—document

**Follow-ups:**
- Mode 0..3 timing
- Word size 16-bit

---

### C143 — SPI IRQ byte state machine

**Interview prompt:**  
Drive SPI transfer via interrupts with a state machine tracking remaining bytes.

**Implement:**
```c
int spi_transfer_irq(const uint8_t *tx, uint8_t *rx, size_t n);
void spi_isr(void);
```

**Constraints / expectations:**
- Completion signal
- Error path

**Follow-ups:**
- DMA upgrade
- Queue of transactions

---

### C144 — SPI multi-device CS

**Interview prompt:**  
Select among multiple CS lines; ensure only one device selected.

**Implement:**
```c
void spi_select(unsigned cs_id);
void spi_deselect(void);
int spi_transfer_cs(unsigned cs_id, const uint8_t *tx, uint8_t *rx, size_t n);
```

**Constraints / expectations:**
- Default idle CS level
- Mutex if multi-thread

**Follow-ups:**
- Shared bus with interrupts
- Timing delays after CS

---

### C145 — I2C write state machine

**Interview prompt:**  
Implement master write: START, addr, data bytes, STOP with ACK checks.

**Implement:**
```c
int i2c_write(uint8_t addr7, const uint8_t *data, size_t n, uint32_t timeout_ms);
```

**Constraints / expectations:**
- NACK handling
- Timeouts each phase

**Follow-ups:**
- 10-bit address
- Repeated start next

---

### C146 — I2C write-then-read (repeated start)

**Interview prompt:**  
Classic sensor transaction: write register address, repeated START, read N bytes.

**Implement:**
```c
int i2c_write_read(uint8_t addr7, const uint8_t *wr, size_t wn,
                   uint8_t *rd, size_t rn, uint32_t timeout_ms);
```

**Constraints / expectations:**
- No STOP between if repeated start
- ACK last byte rules

**Follow-ups:**
- SMBus differences
- Clock stretching wait

---

### C147 — I2C error taxonomy

**Interview prompt:**  
Map NACK/arbitration loss/timeout to distinct error codes and recover bus state.

**Implement:**
```c
typedef enum { I2C_OK, I2C_ENACK, I2C_ETIMEOUT, I2C_EARB, I2C_EBUS } i2c_err_t;
i2c_err_t i2c_write(...);
```

**Constraints / expectations:**
- Leave bus idle on error if possible
- Distinguish addr NACK vs data NACK if HW allows

**Follow-ups:**
- Retries
- Logging

---

### C148 — I2C bus recovery

**Interview prompt:**  
If SDA stuck low, toggle SCL up to 9 times and generate STOP to free the bus.

**Implement:**
```c
int i2c_bus_recover(void);
```

**Constraints / expectations:**
- GPIO bit-bang SCL/SDA
- Return success/fail

**Follow-ups:**
- When to auto-recover
- Device that holds SDA forever

---

### C149 — GPIO driver stubs

**Interview prompt:**  
Implement GPIO get/set/direction and edge IRQ configure against a fake register map.

**Implement:**
```c
void gpio_set_dir(unsigned pin, int output);
void gpio_write(unsigned pin, int level);
int gpio_read(unsigned pin);
void gpio_irq_config(unsigned pin, int rising, int falling, void (*cb)(void));
```

**Constraints / expectations:**
- Pin range checks
- Callback from ISR context

**Follow-ups:**
- Debounce link
- Open-drain

---

### C150 — GPIO debounce state machine

**Interview prompt:**  
Sample or use timers to produce a stable digital output from a bouncing input.

**Implement:**
```c
void debounce_on_edge(void);
int debounce_stable_level(void);
```

**Constraints / expectations:**
- Configurable debounce ms
- No false triggers

**Follow-ups:**
- Integrate with button events
- Analog comparator noise

---

### C151 — PWM period/duty

**Interview prompt:**  
Set PWM frequency and duty cycle given a timer clock.

**Implement:**
```c
int pwm_set(uint32_t clk_hz, uint32_t freq_hz, uint32_t duty_percent);
```

**Constraints / expectations:**
- Integer math careful
- Duty 0..100
- Error if impossible divisors

**Follow-ups:**
- High-res PWM
- Dead-time for H-bridge

---

### C152 — ADC read with averaging

**Interview prompt:**  
Read ADC with settling delay, timeout, optional N-sample average.

**Implement:**
```c
int adc_read_mv(unsigned channel, unsigned samples, uint32_t *mv_out);
```

**Constraints / expectations:**
- Timeout
- Reject invalid channel

**Follow-ups:**
- DMA continuous ADC
- Calibration offset/gain

---

### C153 — Bit-banged UART TX

**Interview prompt:**  
Transmit a byte on a GPIO UART TX line using delays for baud timing (timer mock OK).

**Implement:**
```c
void softuart_tx_byte(uint8_t b);
void softuart_write(const uint8_t *data, size_t n);
```

**Constraints / expectations:**
- Start/stop bits
- Disable IRQ during bit or compensate—discuss

**Follow-ups:**
- RX hard part
- Baud accuracy

---

### C154 — Button long-press / double-click

**Interview prompt:**  
From edge events + time, detect click, double-click, long-press.

**Implement:**
```c
typedef enum { BTN_NONE, BTN_CLICK, BTN_DOUBLE, BTN_LONG } btn_ev_t;
btn_ev_t button_task(uint32_t now_ms, int level);
```

**Constraints / expectations:**
- Configurable thresholds
- Clean state machine

**Follow-ups:**
- Triple click
- Repeat while hold

---

### C155 — Quadrature encoder decode

**Interview prompt:**  
Given two square waves A/B, decode direction and count (Gray-code state table).

**Implement:**
```c
void encoder_update(int a, int b); /* call on change or sample */
int32_t encoder_count(void);
```

**Constraints / expectations:**
- Correct 4x decoding table
- Illegal transitions handled

**Follow-ups:**
- Speed estimation
- Index Z channel

---

### C156 — Shift register bit-bang

**Interview prompt:**  
Drive a 74HC595-like output shift register: data/clock/latch.

**Implement:**
```c
void sr_write8(uint8_t value);
void sr_write_buf(const uint8_t *v, size_t n);
```

**Constraints / expectations:**
- Timing order correct
- Latch once per frame

**Follow-ups:**
- Daisy chain
- SPI HW instead

---

### C157 — 1-Wire reset + read byte

**Interview prompt:**  
Implement reset/presence pulse and read a byte with timing slots (delay stubs provided).

**Implement:**
```c
int ow_reset(void); /* 1 presence, 0 none, <0 error */
uint8_t ow_read_byte(void);
void ow_write_byte(uint8_t b);
```

**Constraints / expectations:**
- Document timing constants
- Bit order

**Follow-ups:**
- Search ROM
- CRC of ROM

---

### C158 — Multi-instance driver context

**Interview prompt:**  
Refactor a UART driver that used globals into `struct uart *` instance pointers.

**Implement:**
```c
typedef struct uart uart_t;
int uart_init(uart_t *u, uintptr_t mmio_base, ring_t *rx, ring_t *tx);
int uart_write(uart_t *u, const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- No globals
- Reentrant across instances

**Follow-ups:**
- Container_of from ISR
- Probe/remove

---

### C159 — Idempotent init/deinit

**Interview prompt:**  
init() may be called twice; deinit() may be called without init. Make safe.

**Implement:**
```c
int uart_init(uart_t *u, ...);
void uart_deinit(uart_t *u);
```

**Constraints / expectations:**
- State flag
- Free resources once

**Follow-ups:**
- Partial init failure
- re-init after fault

---

### C160 — Non-blocking read/write EAGAIN

**Interview prompt:**  
Implement non-blocking APIs returning would-block when rings empty/full.

**Implement:**
```c
int uart_read_nb(uart_t *u, uint8_t *b, size_t n); /* return bytes or -EAGAIN */
int uart_write_nb(uart_t *u, const uint8_t *b, size_t n);
```

**Constraints / expectations:**
- Defined error codes
- No busy spin

**Follow-ups:**
- poll readiness
- POSIX analogy

---


---

[← Back to category index](./README.md)
