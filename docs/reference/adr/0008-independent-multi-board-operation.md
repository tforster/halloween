# ADR-008: Multi-Board Independent Operation <!-- omit in toc -->

**Status:** Superseded by [ADR-009](./0009-single-controller-for-multiple-rigs.md) (2026 season). Accepted for 2025.

**Context:**  
2025 goal was deploying three boards across a larger display area; two ran on the night ([2025 Retrospective](../../explanation/2025-retrospective.md)). Options:

1. **Synchronised:** All boards trigger simultaneously (requires wireless communication)
2. **Master/Slave:** One board controls others (complex wiring)
3. **Independent:** Each board operates autonomously with random timing

**Decision:**  
Independent boards, each with own random trigger timing.

**Rationale:**

- **Simpler implementation:** No wireless protocol, no inter-board communication
- **More natural effect:** Real storms have multiple lightning strikes at different locations
- **Fault tolerance:** One board failure doesn't affect others
- **Easier testing:** Can develop/test single board in isolation
- **Scalable:** Can add more boards without code changes
- **Cost-effective:** No additional wireless hardware required

**Hardware:**

- One complete board assembly per rig (Pico 2, MP3 module, NeoPixels, amplifier)
- Each board has own power supplies
- Each board operates on own random interval timer
- No physical connection between boards

**Consequences:**

- Boards will NOT be synchronised (this is a feature, not a bug!)
- Must manage a separate deployment per board
- Troubleshooting requires checking each board individually
- Software updates must be applied to every board

[← Back to ADR index](./README.md)
