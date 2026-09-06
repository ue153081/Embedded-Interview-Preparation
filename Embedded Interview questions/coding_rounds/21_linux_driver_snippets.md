# Linux Driver Coding Snippets

**IDs:** C286–C300 (15 questions)  
**Focus:** probe/fops/ioctl/poll/sysfs/IRQ/DMA/DT/runtime PM/mmap/debugfs.

[← Back to category index](./README.md)

---

### C286 — platform_driver probe/remove

**Interview prompt:**  
Write a Linux platform_driver skeleton with probe/remove using managed resources.

**Implement:**
```c
static int my_probe(struct platform_device *pdev);
static void my_remove(struct platform_device *pdev);
/* module_platform_driver */
```

**Constraints / expectations:**
- devm_kzalloc
- Error unwind

**Follow-ups:**
- DT match table
- runtime PM stub

---

### C287 — Char device fops

**Interview prompt:**  
Implement open/read/write/release for a simple misc/char device backed by a kernel buffer.

**Implement:**
```c
static ssize_t my_read(struct file *f, char __user *buf, size_t n, loff_t *ppos);
static ssize_t my_write(struct file *f, const char __user *buf, size_t n, loff_t *ppos);
```

**Constraints / expectations:**
- copy_to_user/copy_from_user
- Bounds

**Follow-ups:**
- nonseekable
- concurrency

---

### C288 — Bounded copy_to_user path

**Interview prompt:**  
Read path must not overflow kernel buffer or userspace count.

**Implement:**
```c
ssize_t safe_read(...);
```

**Constraints / expectations:**
- min_t sizes
- return values POSIX-like

**Follow-ups:**
- partial reads
- EFAULT

---

### C289 — Versioned ioctl

**Interview prompt:**  
Define ioctl with struct that includes version; reject unsupported versions.

**Implement:**
```c
struct my_ioctl_arg { uint32_t ver; uint32_t val; };
#define MY_IOC _IOWR('m', 1, struct my_ioctl_arg)
long my_ioctl(struct file *f, unsigned cmd, unsigned long arg);
```

**Constraints / expectations:**
- copy_from_user first
- compat note optional

**Follow-ups:**
- extensible trailing data
- IOC macros

---

### C290 — poll / wait_queue data ready

**Interview prompt:**  
Implement poll that waits until data available; wake from IRQ.

**Implement:**
```c
static __poll_t my_poll(struct file *f, poll_table *wait);
void my_irq(void); /* wakes */
```

**Constraints / expectations:**
- poll_wait
- EPOLLIN when data

**Follow-ups:**
- EPOLLET edge
- fasync

---

### C291 — sysfs error counter

**Interview prompt:**  
Expose an error counter via sysfs show/store (store clears).

**Implement:**
```c
static ssize_t err_show(...);
static ssize_t err_store(...);
```

**Constraints / expectations:**
- DEVICE_ATTR
- Permissions

**Follow-ups:**
- debugfs vs sysfs
- atomic counter

---

### C292 — Threaded IRQ

**Interview prompt:**  
Request threaded IRQ: primary quick handler wakes thread handler.

**Implement:**
```c
static irqreturn_t primary(int irq, void *dev);
static irqreturn_t threaded(int irq, void *dev);
/* request_threaded_irq */
```

**Constraints / expectations:**
- IRQ_WAKE_THREAD
- No sleeping in primary

**Follow-ups:**
- oneshot
- affinity

---

### C293 — dma_alloc_coherent path

**Interview prompt:**  
Allocate coherent DMA buffer and handle failure; free on remove.

**Implement:**
```c
int alloc_dma(struct device *dev);
void free_dma(struct device *dev);
```

**Constraints / expectations:**
- dma_addr_t stored
- GFP flags

**Follow-ups:**
- streaming DMA map API
- attrs

---

### C294 — DT property parse

**Interview prompt:**  
Read a u32 frequency and optional GPIO from device tree in probe.

**Implement:**
```c
int parse_dt(struct device *dev, struct my_cfg *cfg);
```

**Constraints / expectations:**
- device_property_read_u32
- optional gpio_desc

**Follow-ups:**
- graph bindings skip
- endian in DT

---

### C295 — runtime PM suspend/resume

**Interview prompt:**  
Implement runtime suspend/resume callbacks and get/put usage in open/release.

**Implement:**
```c
static int my_runtime_suspend(struct device *dev);
static int my_runtime_resume(struct device *dev);
```

**Constraints / expectations:**
- pm_runtime_get_sync in open
- autosuspend optional

**Follow-ups:**
- system sleep vs runtime
- errors

---

### C296 — mmap kernel buffer

**Interview prompt:**  
Allow userspace to mmap a kernel buffer (vm_ops simplified / remap_pfn_range).

**Implement:**
```c
static int my_mmap(struct file *f, struct vm_area_struct *vma);
```

**Constraints / expectations:**
- Size checks
- VM_DONTEXPAND etc comments

**Follow-ups:**
- coherent DMA mmap
- cache attributes

---

### C297 — miscdevice event notify

**Interview prompt:**  
Register a miscdevice and support fasync or read-queue wakeups for events.

**Implement:**
```c
/* misc_register + fasync or wait queue */
```

**Constraints / expectations:**
- One of fasync/read OK
- Document API

**Follow-ups:**
- netlink alternative
- uevent

---

### C298 — debugfs register dump

**Interview prompt:**  
Create a debugfs file that dumps device registers when read.

**Implement:**
```c
static ssize_t regs_read(...);
/* debugfs_create_file */
```

**Constraints / expectations:**
- safe if device gone
- limit size

**Follow-ups:**
- seq_file
- access control

---

### C299 — Module param + locked state

**Interview prompt:**  
Module param sets mode; protect shared state with spinlock.

**Implement:**
```c
static int mode;
module_param(mode, int, 0644);
/* accessors with locking */
```

**Constraints / expectations:**
- sysfs param concurrency
- validate range

**Follow-ups:**
- rwlock
- percpu

---

### C300 — Fix TOCTOU on userspace length

**Interview prompt:**  
Userspace passes length then buffer; show TOCTOU bug and write the safe pattern (copy length once, clamp, then copy).

**Implement:**
```c
ssize_t buggy_write(...);
ssize_t safe_write(...);
```

**Constraints / expectations:**
- Single copy of metadata
- Clamp to kbuf

**Follow-ups:**
- get_user vs copy_from_user
- Speculative copy concerns

---

---

## Tier S — first 80 (highest MNC frequency)

C006 C013 C021 C022 C031 C036 C041 C042 C056 C057  
C071 C072 C074 C077 C087 C091 C093 C095 C101 C105  
C111 C115 C121 C122 C124 C137 C138 C145 C146 C148  
C150 C155 C164 C165 C166 C167 C173 C174 C175 C181  
C186 C187 C202 C208 C214 C219 C220 C231 C241 C245  
C251 C254 C255 C261 C264 C273 C278 C286 C288 C289  
C290 C292 C010 C014 C067 C082 C118 C134 C141 C160  
C196 C211 C226 C242 C249 C270 C283 C294  

Master these cold before grinding the rest.

---

## Progress

- Elaborated questions completed from blank: ___ / 300  
- Tier S completed: ___ / 80  
- Timed mocks: ___


---

[← Back to category index](./README.md)
