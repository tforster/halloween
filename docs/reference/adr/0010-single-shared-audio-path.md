# ADR-010: Single Shared Audio Path, Latest Strike Wins <!-- omit in toc -->

**Status:** Accepted (2026 season)

**Context:**
Two rigs strike on independent timers, so their strikes sometimes overlap. In 2025 each board had its own DFPlayer, amplifier and speaker ([ADR-006](./0006-external-mp3-player-module.md)). For 2026 the speaker sits with the controller between the rigs ([ADR-009](./0009-single-controller-for-multiple-rigs.md)), and one speaker cannot tell a listener which rig struck. Options:

1. **One audio path per rig:** two DFPlayers, amplifiers and speakers. Twice the audio hardware for no audible difference from the centre.
2. **One audio path, queue overlapping thunder:** the second strike's thunder plays after the first ends, by then long after its lightning.
3. **One audio path, latest strike wins:** a strike during playing thunder replaces it with a new track.

**Decision:**
One DFPlayer Mini, one 60 W TPA3118 mono amplifier and one speaker serve both rigs. Every strike asks a shared thunder channel to play a random track; a track already playing is replaced and nothing queues. The amplifier is fed from the DFPlayer's line-level DAC_L and DAC_R outputs, summed through two 10 kΩ resistors into its mono IN+, with IN− to ground. The DFPlayer's SPK_1/SPK_2 speaker driver stays unwired. The wiring is in the [WireViz harness](../assets/wiring.yml).

**Rationale:**

- **Half the audio hardware:** one MP3 player, amplifier, speaker and 12 V supply
- **Every strike is heard:** replacing the playing track sounds like a fresh roll of thunder, and thunder never trails its lightning
- **Rare in practice:** two 60–120 s timers with sub-second strikes collide only occasionally
- **Clean signal:** DAC_L/DAC_R is line level, meant for an external amplifier; SPK_1/SPK_2 is the DFPlayer's own 3 W bridged speaker output, which the 2025 guide wrongly recommended
- **No cancellation:** summing both channels into IN+ keeps a stereo track whole, whereas DAC_L into IN+ and DAC_R into IN− would subtract one channel from the other and cancel the thunder

**Consequences:**

- A strike that lands during another's thunder cuts it short; this is the intended sound
- Volume (25/30 in 2025, set for one speaker per board) may need retuning on site
- The amp's input terminals are taken from its 2-position input block; check them against the board's silkscreen during the bench test

[← Back to ADR index](./README.md)
