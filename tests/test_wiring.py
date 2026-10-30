"""
The WireViz harness in docs/reference/assets/wiring.yml, read as data.

Expected values come from the 2026 blueprint (docs/explanation/2026-blueprint.md, section 4.1), the
HALL-4 grilling answers and the HALL-8 corrections (ADR-013), not from the YAML: supplies, pins, the
2.7 m data limit, the DAC_L/DAC_R amp feed, and the reused BSS138 level shifter with no fuses or
manual trigger.
"""

from pathlib import Path

import yaml
from wireviz.wireviz import parse

HARNESS_PATH = (
    Path(__file__).resolve().parent.parent / "docs" / "reference" / "assets" / "wiring.yml"
)


def loadHarness():
    return yaml.safe_load(HARNESS_PATH.read_text(encoding="utf-8"))


def pinNumbers(connector):
    return connector.get("pins") or list(range(1, len(connector["pinlabels"]) + 1))


def pinLabel(connector, pin):
    return connector["pinlabels"][pinNumbers(connector).index(pin)]


def asList(value):
    return value if isinstance(value, list) else [value]


def connectionSteps(connectionSet):
    """The (designator, pins) steps of one connection set, skipping the arrows between mates."""
    return [next(iter(step.items())) for step in connectionSet if isinstance(step, dict)]


def buildNets(harness):
    """
    Groups every connector pin into electrical nets, as a parent map over "DESIGNATOR:pin" nodes.

    A connection set lists connectors and cables in turn; each position along it is one wire, so the
    pins on either side of the same wire share a net. An arrow between two connectors (a WireViz
    mate) joins them directly, as a fuse screwed onto a supply terminal does, and a connector's
    loops are jumpers between its own pins. Pins with the same label on one connector (a strip's
    two GND pads, a terminal block's bus) are joined by the part itself.
    """
    parent = {}

    def find(node):
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    def join(first, second):
        parent[find(first)] = find(second)

    connectors = harness["connectors"]
    for name, connector in connectors.items():
        byLabel = {}
        for pin in pinNumbers(connector):
            node = f"{name}:{pin}"
            find(node)
            byLabel.setdefault(pinLabel(connector, pin), []).append(node)
        for nodes in byLabel.values():
            for node in nodes[1:]:
                join(nodes[0], node)
        for first, second in connector.get("loops", []):
            join(f"{name}:{first}", f"{name}:{second}")

    for connectionSet in harness["connections"]:
        steps = connectionSteps(connectionSet)
        width = max(len(asList(points)) for _, points in steps)
        for position in range(width):
            previous = None
            for name, points in steps:
                points = asList(points)
                point = points[position if len(points) > 1 else 0]
                node = f"{name}:{point}" if name in connectors else f"cable {name}:{point}"
                if previous is not None:
                    join(previous, node)
                previous = node
    return find


def pinNumber(harness, name, label):
    connector = harness["connectors"][name]
    for pin in pinNumbers(connector):
        if pinLabel(connector, pin) == label:
            return pin
    raise AssertionError(f"{name} has no pin labelled {label}")


def pinNode(harness, name, label):
    return f"{name}:{pinNumber(harness, name, label)}"


def connected(harness, first, second):
    find = buildNets(harness)
    return find(pinNode(harness, *first)) == find(pinNode(harness, *second))


# Every supply and the input it feeds directly, from blueprint section 4.1: no fuses are fitted in
# 2026.
SUPPLIES = {
    "PSU_L": ("+5V", ("DFP", "VCC")),
    "PSU_A1": ("+5V", ("STRIP_A", "+5V px1")),
    "PSU_A2": ("+5V", ("STRIP_A", "+5V px151")),
    "PSU_B1": ("+5V", ("STRIP_B", "+5V px1")),
    "PSU_B2": ("+5V", ("STRIP_B", "+5V px151")),
    "PSU_AMP": ("+12V", ("AMP", "+12V")),
}


def test_hall8_ac2_no_fuses_and_each_supply_feeds_its_load_directly():
    harness = loadHarness()
    connectors = harness["connectors"]
    supplies = {
        name for name, part in connectors.items() if part.get("type", "").startswith("Power supply")
    }
    assert supplies == set(SUPPLIES)
    assert not [
        name for name, part in connectors.items() if part.get("type", "").startswith("Fuse")
    ]
    for supply, (rail, load) in SUPPLIES.items():
        assert connected(harness, (supply, rail), load), f"{supply} {rail} should feed {load}"


# Every part with a ground, from blueprint section 4.1: all grounds are common.
GROUNDED_PARTS = [*SUPPLIES, "PICO", "U1", "DFP", "AMP", "STRIP_A", "STRIP_B"]


def test_ac2_every_ground_is_common():
    harness = loadHarness()
    find = buildNets(harness)
    grounds = {find(pinNode(harness, part, "GND")) for part in GROUNDED_PARTS}
    assert len(grounds) == 1, "every supply, module and strip ground should share one net"


def cablesBetween(harness, first, second):
    """Names the cables in any connection set that runs from the first connector to the second."""
    found = set()
    for connectionSet in harness["connections"]:
        names = [name for name, _ in connectionSteps(connectionSet)]
        for index in range(len(names) - 2):
            if names[index] == first and names[index + 2] == second:
                found.add(names[index + 1])
    return found


# Rig data path from blueprint section 4.1 and ADR-013: GPIO, BSS138 level shifter channel (low side
# in, high side out), 330 ohm series resistor at the strip's data input.
RIGS = {
    "STRIP_A": {"gpio": "GP16", "shifterIn": "LV1", "shifterOut": "HV1", "resistor": "R_A"},
    "STRIP_B": {"gpio": "GP17", "shifterIn": "LV2", "shifterOut": "HV2", "resistor": "R_B"},
}


def test_ac2_each_rig_data_runs_through_the_level_shifter_and_a_330_ohm_resistor():
    harness = loadHarness()
    for strip, rig in RIGS.items():
        resistor = rig["resistor"]
        assert connected(harness, ("PICO", rig["gpio"]), ("U1", rig["shifterIn"]))
        assert connected(harness, ("U1", rig["shifterOut"]), (resistor, "IN"))
        assert connected(harness, (resistor, "OUT"), (strip, "DIN"))
        assert not connected(
            harness, ("U1", rig["shifterOut"]), (strip, "DIN")
        ), "resistor is bypassed"
        assert "330" in harness["connectors"][resistor]["subtype"]


def test_ac2_each_data_run_is_a_data_and_ground_pair_of_at_most_2_7_m():
    harness = loadHarness()
    for strip, rig in RIGS.items():
        runs = cablesBetween(harness, "U1", rig["resistor"])
        assert len(runs) == 1, f"{strip} should have one data cable from the level shifter"
        run = runs.pop()
        cable = harness["cables"][run]
        assert 0 < cable["length"] <= 2.7
        assert run in cablesBetween(
            harness, "TB_GND", strip
        ), f"{run} should carry a ground to {strip}"


def isWired(harness, name, label):
    """True when any connection set, mates included, touches the pin, so it is not left unwired."""
    pin = pinNumber(harness, name, label)
    return any(
        stepName == name and pin in asList(points)
        for connectionSet in harness["connections"]
        for stepName, points in connectionSteps(connectionSet)
    )


def test_ac3_amp_is_fed_from_dac_l_and_dac_r_summed_into_its_mono_input():
    harness = loadHarness()
    resistors = [
        name for name, part in harness["connectors"].items() if part.get("type") == "Resistor"
    ]
    for channel in ("DAC_L", "DAC_R"):
        summing = [
            name
            for name in resistors
            if connected(harness, ("DFP", channel), (name, "IN"))
            and connected(harness, (name, "OUT"), ("AMP", "IN+"))
        ]
        assert (
            len(summing) == 1
        ), f"{channel} should reach the amp's IN+ through one summing resistor"
        assert "10 k" in harness["connectors"][summing[0]]["subtype"]
    assert connected(harness, ("AMP", "IN-"), ("DFP", "GND"))


def test_ac3_dfplayer_speaker_outputs_are_not_wired():
    harness = loadHarness()
    assert not isWired(harness, "DFP", "SPK_1")
    assert not isWired(harness, "DFP", "SPK_2")


def test_ac2_amp_drives_one_speaker():
    harness = loadHarness()
    assert connected(harness, ("AMP", "OUT+"), ("SPK", "+"))
    assert connected(harness, ("AMP", "OUT-"), ("SPK", "-"))


def test_ac2_dfplayer_takes_commands_on_uart1_tx_gp4():
    harness = loadHarness()
    assert connected(harness, ("PICO", "GP4"), ("DFP", "RX"))


def test_ac2_pico_runs_from_the_logic_rail_through_a_schottky_into_vsys_never_vbus():
    harness = loadHarness()
    diodes = [name for name, part in harness["connectors"].items() if part.get("type") == "Diode"]
    feeds = [
        name
        for name in diodes
        if connected(harness, (name, "A"), ("DFP", "VCC"))
        and connected(harness, (name, "K"), ("PICO", "VSYS"))
    ]
    assert len(feeds) == 1
    assert "Schottky" in harness["connectors"][feeds[0]]["subtype"]
    assert not isWired(harness, "PICO", "VBUS")


def test_hall8_ac1_level_shifter_bridges_the_3v3_and_5_v_rails():
    harness = loadHarness()
    assert "BSS138" in harness["connectors"]["U1"]["subtype"]
    assert connected(harness, ("U1", "HV"), ("DFP", "VCC")), "HV is the 5 V side"
    assert connected(harness, ("U1", "LV"), ("PICO", "3V3")), "LV is the Pico's 3.3 V side"


def test_hall8_ac1_each_used_high_side_channel_has_a_1_5_kohm_pull_up_to_hv():
    # The board's own 10 kohm pull-ups rise too slowly to drive 2.7 m of cable at 800 kHz; a
    # 1.5 kohm in parallel speeds the edge while keeping the Pico's sink current under 4 mA.
    harness = loadHarness()
    for rig in RIGS.values():
        pullUps = [
            part["subtype"]
            for name, part in harness["connectors"].items()
            if part.get("type") == "Resistor"
            and connected(harness, (name, "IN"), ("U1", rig["shifterOut"]))
            and connected(harness, (name, "OUT"), ("U1", "HV"))
        ]
        assert len(pullUps) == 1, f"{rig['shifterOut']} needs one pull-up to HV"
        assert pullUps[0].startswith("1.5 kohm")


def test_hall8_ac2_manual_trigger_is_not_fitted():
    harness = loadHarness()
    assert "SW1" not in harness["connectors"]
    assert "R_PD" not in harness["connectors"]
    assert "GP15" not in harness["connectors"]["PICO"]["pinlabels"]


def test_net_helpers_catch_a_miswired_harness():
    # The checks above are only as good as the netlist; break the real harness and confirm they see it.
    harness = loadHarness()
    harness["connections"].append([{"DFP": [6]}, {"W_AUDIO": [1]}, {"R_SUM_L": [1]}])
    harness["connections"].remove([{"TB_GND": [8]}, {"W_AMP_GND": [1]}, {"AMP": [2]}])
    assert isWired(harness, "DFP", "SPK_1")
    assert not connected(harness, ("AMP", "GND"), ("PICO", "GND"))


def test_ac2_every_wire_states_its_gauge():
    harness = loadHarness()
    for name, cable in harness["cables"].items():
        assert str(cable.get("gauge", "")).endswith("AWG"), f"{name} has no AWG gauge"


def test_ac1_harness_renders_and_the_committed_svg_matches_it(tmp_path):
    # Renders with the same call `npm run wiring` makes; needs Graphviz's `dot` on the PATH.
    parse(HARNESS_PATH, output_formats=("svg",), output_dir=tmp_path, output_name="wiring")
    rendered = (tmp_path / "wiring.svg").read_text(encoding="utf-8")
    committed = HARNESS_PATH.with_suffix(".svg").read_text(encoding="utf-8")
    assert rendered == committed, "wiring.svg is stale: run `npm run wiring` and commit the result"
