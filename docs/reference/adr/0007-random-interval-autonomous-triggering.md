# ADR-007: Random Interval Autonomous Triggering <!-- omit in toc -->

**Status:** Accepted

**Context:**  
2024 version required manual triggering via switch/sensor. For 2025, want more immersive "storm" atmosphere that doesn't require audience interaction or line-of-sight to sensors.

**Decision:**  
Implement random interval triggering: system automatically fires effect every 60-120 seconds.

**Rationale:**

- **More realistic:** Real storms are unpredictable
- **Better ambiance:** Continuous operation throughout evening
- **No user interaction needed:** Works even when no one is nearby
- **Simpler hardware:** No trigger sensors required (optional feature)
- **Testing-friendly:** Can still support manual trigger for development

**Implementation:**

```python
import random
import time

def autonomous_mode():
    while True:
        interval = random.randint(60, 120)  # 60-120 seconds
        time.sleep(interval)
        trigger_effect()
```

**Consequences:**

- Need reliable random number generator
- Must handle edge cases (no rapid re-triggering if interval is too short)
- Power consumption slightly higher (always-on operation)
- Testing takes longer (must wait for random triggers)
- Can add manual trigger as override for testing

[← Back to ADR index](./README.md)
