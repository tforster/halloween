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
