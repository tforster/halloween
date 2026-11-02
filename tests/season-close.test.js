// season-close.test.js — guards the 2026 season close set by HALL-11
//
// Halloween 2026 ran thunder only: one rig's timer on a fixed 30 s, its strip disconnected, because the
// strips' data signal was corrupt on the night. HALL-11 commits that as-run config, records the season in
// a retrospective and closes it in the README and CHANGELOG, so the 2026 tag freezes what actually ran.

// System dependencies
import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { readFile, access } from "node:fs/promises";
import path from "node:path";

const repoRoot = path.resolve(import.meta.dirname, "..");
const retrospective = "docs/explanation/2026-retrospective.md";

// The as-built photos taken on 2026-10-31, kept as the record of the enclosure that ran.
const asBuiltPhotos = ["as-built-2026-enclosure.jpg", "as-built-2026-amp.jpg", "as-built-2026-pico.jpg"];

/**
 * Reads a repo file as UTF-8.
 *
 * @param {string} file - Repo-relative path.
 * @returns {Promise<string>} File contents.
 */
async function readRepoFile(file) {
  return readFile(path.join(repoRoot, file), "utf8");
}

describe("HALL-11: 2026 season close", () => {
  it("AC1: src/main.py holds the as-run config, one rig on a fixed 30 s timer", async () => {
    const main = await readRepoFile("src/main.py");
    const rigs = main.match(/^RIGS = \[\n([\s\S]*?)^\]/m);
    assert.ok(rigs, "RIGS list not found");
    const entries = rigs[1].match(/\{"name"/g) ?? [];
    assert.strictEqual(entries.length, 1, "one rig drives the thunder");
    assert.match(rigs[1], /"intervalS": \(30, 30\)/);
    assert.match(main, /^TEST_MODE = False/m);
  });

  it("AC2: the retrospective exists, is indexed, links the as-built photos and lists the 2027 actions", async () => {
    const doc = await readRepoFile(retrospective);
    const index = await readRepoFile("docs/explanation/README.md");
    assert.match(index, /\(\.\/2026-retrospective\.md\)/);
    for (const photo of asBuiltPhotos) {
      await access(path.join(repoRoot, "docs/reference/assets", photo));
      assert.ok(doc.includes(`../reference/assets/${photo}`), `${photo} not linked`);
    }
    assert.match(doc, /## \d+\. 2027 Actions/);
    assert.match(doc, /## \d+\. Carried-Over Fixes/);
  });

  it("AC7: the 2025 retrospective replaces Design Challenges and every doc says 2025 ran two boards", async () => {
    const doc = await readRepoFile("docs/explanation/2025-retrospective.md");
    const index = await readRepoFile("docs/explanation/README.md");
    assert.match(index, /\(\.\/2025-retrospective\.md\)/);
    assert.doesNotMatch(index, /design-challenges/);
    await assert.rejects(access(path.join(repoRoot, "docs/explanation/design-challenges.md")));
    assert.match(doc, /## \d+\. 2026 Actions/);
    for (const file of [
      "README.md",
      "CHANGELOG.md",
      "CLAUDE.md",
      "docs/explanation/2026-blueprint.md",
      "docs/reference/adr/0009-single-controller-for-multiple-rigs.md",
    ]) {
      const text = await readRepoFile(file);
      assert.doesNotMatch(
        text,
        /three (independent|complete) (Pico )?boards|3 independent units|nine (power )?supplies/i,
        `${file} still says 2025 had three boards`
      );
    }
  });

  it("AC3: README and CHANGELOG close 2026, and no doc calls it in progress", async () => {
    const readme = await readRepoFile("README.md");
    const changelog = await readRepoFile("CHANGELOG.md");
    const claude = await readRepoFile("CLAUDE.md");
    assert.match(readme, /^\| 2026 \|.*\[`2026` tag\]/m);
    assert.match(changelog, /^## v2026 /m);
    for (const [name, text] of [
      ["README.md", readme],
      ["CLAUDE.md", claude],
    ]) {
      assert.doesNotMatch(text, /2026 is in progress|design in progress/i, `${name} still calls 2026 in progress`);
    }
  });
});
