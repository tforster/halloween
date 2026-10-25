# Architecture Decision Records <!-- omit in toc -->

Why the project is built the way it is, one decision per file. ADR-001 to ADR-004 cover the 2024 ESP32 build and live with the [`2024` tag](https://github.com/tforster/halloween/tree/2024). The 2026 decisions (ADR-009 onwards) are added as the [2026 blueprint](../../explanation/2026-blueprint.md#43-documentation-and-diagrams) is built.

## Table of Contents <!-- omit in toc -->

- [1. Records](#1-records)
- [2. Adding a Record](#2-adding-a-record)

## 1. Records

| ADR                                                        | Decision                                               | Status                 |
| :--------------------------------------------------------- | :----------------------------------------------------- | :--------------------- |
| [ADR-005](./0005-migrate-from-esp32-to-pico-2.md)          | Migration from ESP32 to Raspberry Pi Pico 2 (2025)     | Accepted (2025 season) |
| [ADR-006](./0006-external-mp3-player-module.md)            | External MP3 Player Module for Audio                   | Accepted               |
| [ADR-007](./0007-random-interval-autonomous-triggering.md) | Random Interval Autonomous Triggering                  | Accepted               |
| [ADR-008](./0008-independent-multi-board-operation.md)     | Multi-Board Independent Operation                      | Accepted               |
| [ADR-011](./0011-asyncio-scheduling.md)                    | asyncio Scheduling                                     | Accepted (2026 season) |
| [ADR-012](./0012-wireviz-and-wokwi.md)                     | WireViz and Wokwi for Hardware Diagrams and Simulation | Accepted (2026 season) |

## 2. Adding a Record

- Name the file `NNNN-slug.md`, continuing the numbering, and add it to the table above.
- Give it Status, Context, Decision, Rationale and Consequences, as the existing records do.
- A record keeps its number for good. When a decision no longer holds, set its status to superseded by the new ADR rather than deleting it.

[← Back to Reference](../README.md)
