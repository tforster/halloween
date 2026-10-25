# ADR-008: Multi-Board Independent Operation <!-- omit in toc -->

**Status:** Accepted

**Context:**  
2025 goal is deploying 3 boards across larger display area. Options:

1. **Synchronised:** All boards trigger simultaneously (requires wireless communication)
2. **Master/Slave:** One board controls others (complex wiring)
3. **Independent:** Each board operates autonomously with random timing

**Decision:**  
Three independent boards, each with own random trigger timing.

**Rationale:**

- **Simpler implementation:** No wireless protocol, no inter-board communication
- **More natural effect:** Real storms have multiple lightning strikes at different locations
- **Fault tolerance:** One board failure doesn't affect others
- **Easier testing:** Can develop/test single board in isolation
- **Scalable:** Can add more boards without code changes
- **Cost-effective:** No additional wireless hardware required

**Hardware:**

- 3x complete board assemblies (Pico 2, MP3 module, NeoPixels, amplifier)
- Each board has own power supplies
- Each board operates on own random interval timer
- No physical connection between boards

**Consequences:**

- Boards will NOT be synchronised (this is a feature, not a bug!)
- Must manage 3 separate deployments
- Troubleshooting requires checking each board individually
- Software updates must be applied to all 3 boards

[← Back to ADR index](./README.md)
