# Interrupt-Driven UART Driver with Ring Buffer + Event Queue

### Embedded Systems Interview Preparation

------------------------------------------------------------------------

# 1. Overview

This document explains how to design a **production-style
interrupt-driven UART driver** using:

-   **Ring Buffers (Circular Buffers)** for TX and RX
-   **Event Queue** for asynchronous processing
-   **Interrupt Service Routines (ISR)** for UART hardware interaction

This architecture is extremely common in **bare‑metal firmware and RTOS
systems** and is frequently asked in **embedded software interviews**
(ARM, Qualcomm, NVIDIA, etc.).

------------------------------------------------------------------------

# 2. High Level Architecture

                    +-------------------+
                    |   Application     |
                    +---------+---------+
                              |
                              v
                         Event Queue
                              |
                              v
                          UART Driver
                    +--------+--------+
                    |                 |
                    v                 v
               TX Ring Buffer     RX Ring Buffer
                    |                 |
                    v                 v
                  UART TX ISR       UART RX ISR
                         \           /
                          \         /
                           +-------+
                           | UART  |
                           | HW    |
                           +-------+

Key principles:

-   **RX Interrupt → store byte in RX ring buffer**
-   **TX Interrupt → send next byte from TX ring buffer**
-   **Event queue notifies application when events occur**

This keeps interrupts **short and deterministic**.

------------------------------------------------------------------------

# 3. Ring Buffer Design

Ring buffers provide:

-   O(1) push and pop
-   No dynamic memory allocation
-   Deterministic timing
-   Perfect for interrupt-safe communication

## ring_buffer.h

``` c
#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include <stdint.h>

#define UART_BUFFER_SIZE 128

typedef struct
{
    uint8_t buffer[UART_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} RingBuffer;

void rb_init(RingBuffer *rb);

int rb_push(RingBuffer *rb, uint8_t data);

int rb_pop(RingBuffer *rb, uint8_t *data);

int rb_empty(RingBuffer *rb);

int rb_full(RingBuffer *rb);

#endif
```

------------------------------------------------------------------------

## ring_buffer.c

``` c
#include "ring_buffer.h"

void rb_init(RingBuffer *rb)
{
    rb->head = 0;
    rb->tail = 0;
}

int rb_empty(RingBuffer *rb)
{
    return rb->head == rb->tail;
}

int rb_full(RingBuffer *rb)
{
    return ((rb->head + 1) % UART_BUFFER_SIZE) == rb->tail;
}

int rb_push(RingBuffer *rb, uint8_t data)
{
    uint16_t next = (rb->head + 1) % UART_BUFFER_SIZE;

    if(next == rb->tail)
        return -1;

    rb->buffer[rb->head] = data;
    rb->head = next;

    return 0;
}

int rb_pop(RingBuffer *rb, uint8_t *data)
{
    if(rb_empty(rb))
        return -1;

    *data = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % UART_BUFFER_SIZE;

    return 0;
}
```

------------------------------------------------------------------------

# 4. Event Queue System

Event queues allow **interrupts to notify the main loop** without doing
heavy work inside the ISR.

## event_queue.h

``` c
#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include <stdint.h>

#define EVENT_QUEUE_SIZE 16

typedef enum
{
    EVENT_UART_RX,
    EVENT_UART_TX_DONE
} EventType;

typedef struct
{
    EventType type;
    uint32_t data;
} Event;

typedef struct
{
    Event buffer[EVENT_QUEUE_SIZE];
    volatile uint8_t head;
    volatile uint8_t tail;
} EventQueue;

void event_queue_init(EventQueue *q);

int event_push(EventQueue *q, Event e);

int event_pop(EventQueue *q, Event *e);

#endif
```

------------------------------------------------------------------------

## event_queue.c

``` c
#include "event_queue.h"

void event_queue_init(EventQueue *q)
{
    q->head = 0;
    q->tail = 0;
}

int event_push(EventQueue *q, Event e)
{
    uint8_t next = (q->head + 1) % EVENT_QUEUE_SIZE;

    if(next == q->tail)
        return -1;

    q->buffer[q->head] = e;
    q->head = next;

    return 0;
}

int event_pop(EventQueue *q, Event *e)
{
    if(q->head == q->tail)
        return -1;

    *e = q->buffer[q->tail];
    q->tail = (q->tail + 1) % EVENT_QUEUE_SIZE;

    return 0;
}
```

------------------------------------------------------------------------

# 5. UART Driver Design

The driver contains:

-   TX ring buffer
-   RX ring buffer
-   UART APIs
-   ISR handler

## uart_driver.h

``` c
#ifndef UART_DRIVER_H
#define UART_DRIVER_H

#include <stdint.h>
#include "ring_buffer.h"

typedef struct
{
    RingBuffer tx_buffer;
    RingBuffer rx_buffer;
} UART_Driver;

void uart_init(UART_Driver *drv);

int uart_send_byte(UART_Driver *drv, uint8_t data);

void uart_send_buffer(UART_Driver *drv, uint8_t *data, int len);

int uart_read_byte(UART_Driver *drv, uint8_t *data);

void UART_ISR();

#endif
```

------------------------------------------------------------------------

## uart_driver.c

``` c
#include "uart_driver.h"
#include "event_queue.h"

extern EventQueue event_queue;

UART_Driver uart_driver;

#define UART_DR   (*(volatile uint32_t*)0x40000000)
#define UART_SR   (*(volatile uint32_t*)0x40000004)

#define UART_RX_READY  (1 << 0)
#define UART_TX_EMPTY  (1 << 1)

void UART_Enable_TX_Interrupt() {}
void UART_Disable_TX_Interrupt() {}

void uart_init(UART_Driver *drv)
{
    rb_init(&drv->tx_buffer);
    rb_init(&drv->rx_buffer);
}

int uart_send_byte(UART_Driver *drv, uint8_t data)
{
    if(rb_push(&drv->tx_buffer, data) < 0)
        return -1;

    UART_Enable_TX_Interrupt();

    return 0;
}

void uart_send_buffer(UART_Driver *drv, uint8_t *data, int len)
{
    for(int i = 0; i < len; i++)
        uart_send_byte(drv, data[i]);
}

int uart_read_byte(UART_Driver *drv, uint8_t *data)
{
    return rb_pop(&drv->rx_buffer, data);
}

void UART_ISR()
{
    if(UART_SR & UART_RX_READY)
    {
        uint8_t data = UART_DR;

        rb_push(&uart_driver.rx_buffer, data);

        Event e;
        e.type = EVENT_UART_RX;
        event_push(&event_queue, e);
    }

    if(UART_SR & UART_TX_EMPTY)
    {
        uint8_t data;

        if(rb_pop(&uart_driver.tx_buffer, &data) == 0)
        {
            UART_DR = data;
        }
        else
        {
            UART_Disable_TX_Interrupt();

            Event e;
            e.type = EVENT_UART_TX_DONE;
            event_push(&event_queue, e);
        }
    }
}
```

------------------------------------------------------------------------

# 6. Application Layer

## main.c

``` c
#include "uart_driver.h"
#include "event_queue.h"

EventQueue event_queue;

void process_uart_data()
{
    uint8_t byte;

    while(uart_read_byte(&uart_driver, &byte) == 0)
    {
        // Example protocol processing
    }
}

void handle_tx_done()
{
}

int main()
{
    Event e;

    uart_init(&uart_driver);
    event_queue_init(&event_queue);

    while(1)
    {
        if(event_pop(&event_queue, &e) == 0)
        {
            switch(e.type)
            {
                case EVENT_UART_RX:
                    process_uart_data();
                    break;

                case EVENT_UART_TX_DONE:
                    handle_tx_done();
                    break;
            }
        }
    }
}
```

------------------------------------------------------------------------

# 7. Data Flow

## RX Flow

    UART Hardware
         |
         v
    RX Interrupt
         |
         v
    RX Ring Buffer
         |
         v
    Event Queue
         |
         v
    Application Processing

## TX Flow

    Application
         |
         v
    TX Ring Buffer
         |
         v
    TX Interrupt
         |
         v
    UART Hardware

------------------------------------------------------------------------

# 8. Why This Architecture Is Used

Advantages:

-   Non‑blocking UART
-   Low interrupt latency
-   Deterministic execution
-   Clean driver/application separation
-   Scales well in large firmware systems

------------------------------------------------------------------------

# 9. Important Interview Follow‑Ups

### Why keep ISR short?

Long ISRs increase **interrupt latency** and can cause missed
interrupts.

------------------------------------------------------------------------

### What happens if RX buffer overflows?

Possible solutions:

-   Drop incoming byte
-   Overwrite oldest byte
-   Raise overflow flag

------------------------------------------------------------------------

### Why are head and tail marked volatile?

Because they are accessed by:

-   ISR context
-   Main application context

------------------------------------------------------------------------

### Why separate TX and RX buffers?

Because UART transmit and receive operations are **independent data
flows**.

------------------------------------------------------------------------

### Why is TX interrupt disabled when buffer is empty?

To avoid **continuous empty interrupts** when no data remains.

------------------------------------------------------------------------

# 10. Common Advanced Interview Questions

Interviewers may ask:

1.  How would you implement this driver using **DMA instead of
    interrupts**?
2.  How do you support **multiple UART peripherals**?
3.  How would you make this **RTOS‑safe**?
4.  How do you implement **flow control (RTS/CTS)**?
5.  How would you handle **high‑speed UART (10 Mbps)**?

------------------------------------------------------------------------

# 11. Summary

This UART driver demonstrates:

-   Interrupt driven IO
-   Circular buffer data structures
-   Event driven firmware architecture
-   Clean driver abstraction

These patterns are used in **real production firmware and embedded
operating systems**.
