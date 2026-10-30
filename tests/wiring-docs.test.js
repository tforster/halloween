// wiring-docs.test.js — guards the two-rig hardware docs set by HALL-4
//
// HALL-4 moved the hardware docs from three 2025 boards to two rigs on one Pico, corrected the amp
// feed from SPK_1/SPK_2 to DAC_L/DAC_R, and recorded the decisions as ADRs. These tests read the
// docs so a later story cannot bring the 2025 wiring back.

// System dependencies
import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { readFile, readdir } from "node:fs/promises";
import path from "node:path";

const repoRoot = path.resolve(import.meta.dirname, "..");
const adrFolder = path.join(repoRoot, "docs/reference/adr");

// The hardware docs a builder follows: specifications, assembly steps and the parts list.
const hardwareDocs = ["docs/reference/hardware.md", "docs/how-to/assemble-hardware.md", "docs/reference/bill-of-materials.md"];

/**
 * Reads a repo file as UTF-8.
 *
 * @param {string} file - Repo-relative path.
 * @returns {Promise<string>} File contents.
 */
async function readRepoFile(file) {
  return readFile(path.join(repoRoot, file), "utf8");
}

/**
 * Reads the ADR with the given number.
 *
 * @param {string} number - Four-digit ADR number, e.g. "0009".
 * @returns {Promise<string>} The ADR's Markdown.
 */
async function readAdr(number) {
  const file = (await readdir(adrFolder)).find((name) => name.startsWith(`${number}-`));
  assert.ok(file, `ADR-${number.slice(1)} does not exist`);
  return readFile(path.join(adrFolder, file), "utf8");
}

describe("two-rig hardware docs", () => {
  it("HALL-4 AC5: ADR-009 and ADR-010 exist and are indexed", async () => {
    const index = await readRepoFile("docs/reference/adr/README.md");
    assert.match(await readAdr("0009"), /^# ADR-009: .*single controller/im);
    assert.match(await readAdr("0010"), /^# ADR-010: .*latest strike wins/im);
    assert.match(index, /\[ADR-009\]\(\.\/0009-/);
    assert.match(index, /\[ADR-010\]\(\.\/0010-/);
  });

  it("HALL-4 AC5: ADR-008 is superseded by ADR-009", async () => {
    assert.match(await readAdr("0008"), /^\*\*Status:\*\* Superseded by \[ADR-009\]/m);
    const index = await readRepoFile("docs/reference/adr/README.md");
    assert.match(index, /\[ADR-008\].*\|\s*Superseded by ADR-009\s*\|/);
  });

  it("HALL-4 AC5: ADR-012 records the WireViz harness", async () => {
    const adr = await readAdr("0012");
    assert.match(adr, /assets\/wiring\.yml/);
    assert.doesNotMatch(adr, /added by the wiring story/, "ADR-012 still defers WireViz to HALL-4");
  });

  it("HALL-4 AC3: the hardware docs feed the amp from DAC_L/DAC_R and never from SPK_1/SPK_2", async () => {
    for (const file of hardwareDocs) {
      for (const line of (await readRepoFile(file)).split("\n").filter((text) => /SPK_[12]/.test(text))) {
        assert.match(line, /unwired|not |instead/i, `${file} wires SPK_1/SPK_2: ${line.trim()}`);
      }
    }
    assert.match(await readRepoFile("docs/how-to/assemble-hardware.md"), /DAC_L.*DAC_R/);
  });

  it("HALL-4 AC4: the hardware docs describe two rigs on one controller, with no three-board leftovers", async () => {
    for (const file of hardwareDocs) {
      const content = await readRepoFile(file);
      assert.match(content, /two rigs/i, `${file} does not describe two rigs`);
      assert.doesNotMatch(
        content,
        /three boards?|3 boards|per board|board [123]\b|multi-board/i,
        `${file} keeps 2025 board wording`
      );
      assert.doesNotMatch(content, /until this guide is updated/, `${file} still defers to the blueprint`);
    }
  });

  it("HALL-4 AC2: the assembly guide shows the rendered wiring diagram", async () => {
    assert.match(await readRepoFile("docs/how-to/assemble-hardware.md"), /!\[[^\]]+\]\(\.\.\/reference\/assets\/wiring\.svg\)/);
  });
});

// Every part in wiring.yml, as the ASCII diagram names it, from the HALL-7 and HALL-8 acceptance criteria.
const diagramParts = [
  "PSU_L",
  "PSU_A1",
  "PSU_A2",
  "PSU_B1",
  "PSU_B2",
  "PSU_AMP",
  "TB_5V",
  "TB_GND",
  "D1",
  "Pico 2",
  "BSS138 (U1)",
  "DFPlayer Mini",
  "TPA3118",
  "Speaker",
  "Rig A",
  "Rig B",
  "R_PU_A",
  "R_PU_B",
  "R_A",
  "R_B",
  "R_SUM_L",
  "R_SUM_R",
];

// Pin labels as wiring.yml gives them: Pico 2 and DFPlayer physical pins, and the BSS138 board's printed labels.
const diagramPins = [
  "GP4 6",
  "GP16 21",
  "GP17 22",
  "3V3 36",
  "GND 38",
  "VSYS 39",
  "VBUS 40",
  "LV1",
  "HV1",
  "LV2",
  "HV2",
  "LV",
  "HV",
  "GND 7",
  "VCC 1",
  "2 RX",
  "DAC_R 4",
  "DAC_L 5",
];

describe("ASCII wiring diagram", () => {
  const diagramFile = "docs/reference/wiring-diagram.md";

  it("HALL-7 AC1: the diagram is in the reference docs, indexed and linked from the assembly guide", async () => {
    assert.match(await readRepoFile("docs/reference/README.md"), /\]\(\.\/wiring-diagram\.md\)/);
    assert.match(await readRepoFile("docs/how-to/assemble-hardware.md"), /\]\(\.\.\/reference\/wiring-diagram\.md\)/);
  });

  it("HALL-7 AC2: the diagram shows every wiring.yml part with its physical pin numbers", async () => {
    // Collapse runs of spaces so pin labels can be padded for alignment in the drawing.
    const diagram = (await readRepoFile(diagramFile)).replace(/ +/g, " ");
    for (const part of diagramParts) assert.ok(diagram.includes(part), `diagram is missing ${part}`);
    for (const pin of diagramPins) assert.ok(diagram.includes(pin), `diagram is missing pin ${pin}`);
  });

  it("HALL-7 AC3: the diagram defers to wiring.yml", async () => {
    assert.match(await readRepoFile(diagramFile), /\[`wiring\.yml`\]\(\.\/assets\/wiring\.yml\)[^.]*wins/);
  });
});

// The docs a builder follows for the 2026 wiring, which HALL-8 corrected to the parts actually used.
const asBuiltDocs = [...hardwareDocs, "docs/reference/wiring-diagram.md", "docs/explanation/2026-blueprint.md"];

/**
 * Lists the lines of a repo file that match a pattern but not an allowed context.
 *
 * @param {string} file - Repo-relative path.
 * @param {RegExp} pattern - What a line must not describe as fitted.
 * @param {RegExp} allowed - Context that marks the line as a correction or a not-fitted mention.
 * @returns {Promise<string[]>} The offending lines, trimmed.
 */
async function unqualifiedLines(file, pattern, allowed) {
  const lines = (await readRepoFile(file)).split("\n");
  return lines.filter((line) => pattern.test(line) && !allowed.test(line)).map((line) => line.trim());
}

describe("2026 hardware docs", () => {
  // A line may still name a part when it says the part is not fitted, or that naming it was an error.
  const notFitted = /in error|not fitted|no fuses?|unwired|unfused|firmware only/i;

  it("HALL-8 AC3: the docs use the reused BSS138 board, not the 74AHCT125", async () => {
    for (const file of asBuiltDocs) {
      assert.match(await readRepoFile(file), /BSS138/, `${file} does not describe the BSS138 board`);
      assert.deepEqual(await unqualifiedLines(file, /74AHCT125|AHCT/, notFitted), [], `${file} still fits the 74AHCT125`);
    }
  });

  it("HALL-8 AC3: the docs fit no fuses and no manual trigger", async () => {
    for (const file of asBuiltDocs) {
      assert.deepEqual(await unqualifiedLines(file, /\bfuses?\b|\bF_(L|A1|A2|B1|B2|AMP)\b/i, notFitted), [], `${file} fits fuses`);
      assert.deepEqual(
        await unqualifiedLines(file, /\bSW1\b|\bR_PD\b|manual trigger/i, notFitted),
        [],
        `${file} fits a manual trigger`
      );
    }
  });

  it("HALL-8 AC3: the assembly guide shows the labelled level shifter pin photo", async () => {
    assert.match(
      await readRepoFile("docs/how-to/assemble-hardware.md"),
      /!\[[^\]]+\]\(\.\.\/reference\/assets\/level-shifter\.jpg\)/
    );
  });

  it("HALL-8 AC4: known issues covers BSS138 rise time over long runs and the pull-up fix", async () => {
    const knownIssues = await readRepoFile("docs/reference/known-issues.md");
    assert.match(knownIssues, /BSS138/);
    assert.match(knownIssues, /1\.5 kΩ/);
  });

  it("HALL-8 AC5: ADR-013 records the reused BSS138 board as a blueprint correction and is indexed", async () => {
    const adr = await readAdr("0013");
    assert.match(adr, /^# ADR-013: .*BSS138/im);
    for (const topic of [/in error/, /1\.5 kΩ/, /2025/]) assert.match(adr, topic);
    assert.match(await readRepoFile("docs/reference/adr/README.md"), /\[ADR-013\]\(\.\/0013-/);
  });

  it("HALL-8 AC5: the docs treat the 2026 parts as the design, not as deviations from it", async () => {
    for (const file of [...asBuiltDocs, "docs/reference/adr/README.md", "CLAUDE.md"]) {
      assert.doesNotMatch(await readRepoFile(file), /deviat|as.built|restore[^.]*2027/i, `${file} frames 2026 as a deviation`);
    }
  });
});
