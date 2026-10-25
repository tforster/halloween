// repo.test.js — guards the repo conventions set by HALL-2
//
// HALL-2 brought this repo in line with the agents0 repo design: CLAUDE.md for agent context,
// oxlint/oxfmt instead of ESLint/Prettier, Diátaxis docs and no 2025 leftovers. These tests read
// the repo's own files so a later story cannot quietly undo that alignment.

// System dependencies
import { spawnSync } from "node:child_process";
import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { access, readFile, readdir } from "node:fs/promises";
import path from "node:path";

const repoRoot = path.resolve(import.meta.dirname, "..");

/**
 * Reads the root package.json.
 *
 * @returns {Promise<{ scripts: Record<string, string>, devDependencies?: Record<string, string> }>} Parsed manifest.
 */
async function readPackageJson() {
  return JSON.parse(await readFile(path.join(repoRoot, "package.json"), "utf8"));
}

/**
 * Lists the repo's own text files, relative to the repo root, skipping VCS metadata, installed
 * dependencies, gitignored audio and binary assets.
 *
 * @param {RegExp} [pattern] - Only return paths matching this pattern.
 * @returns {Promise<string[]>} Repo-relative paths.
 */
async function listRepoFiles(pattern = /./) {
  const skippedDirs = /(^|\/)(\.git|\.jj|node_modules|venv|\.venv|audio|__pycache__)(\/|$)/;
  const binaryExtensions = /\.(pdf|png|jpe?g|uf2|mp3)$/i;
  const entries = await readdir(repoRoot, { recursive: true, withFileTypes: true });
  return entries
    .filter((entry) => entry.isFile())
    .map((entry) => path.relative(repoRoot, path.join(entry.parentPath, entry.name)))
    .filter((file) => !skippedDirs.test(file) && !binaryExtensions.test(file) && pattern.test(file));
}

/**
 * Removes fenced code blocks, whose headings and links are examples rather than content.
 *
 * @param {string} markdown - Markdown source.
 * @returns {string} The source without fenced blocks.
 */
function stripFences(markdown) {
  return markdown.replace(/^(```|~~~)[^\n]*\n[\s\S]*?^\1[^\n]*$/gm, "");
}

/**
 * Lists the anchors GitHub generates for a document's headings: lowercase, punctuation and emoji
 * dropped, spaces to hyphens, and a -1, -2 suffix on repeats.
 *
 * @param {string} markdown - Markdown source.
 * @returns {Set<string>} Anchor slugs without the leading #.
 */
function headingAnchors(markdown) {
  const anchors = new Set();
  for (const [, text] of stripFences(markdown).matchAll(/^#{1,6} (.+)$/gm)) {
    const base = text
      .replace(/<!--.*?-->/g, "")
      .trim()
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s_-]/gu, "")
      .replace(/\s/g, "-");
    let slug = base;
    for (let repeat = 1; anchors.has(slug); repeat++) slug = `${base}-${repeat}`;
    anchors.add(slug);
  }
  return anchors;
}

describe("repo conventions", () => {
  it("HALL-2 AC6: docs sit in Diátaxis folders, each indexed by its README", async () => {
    const categories = ["explanation", "how-to", "reference", "tutorials"];
    const docsEntries = (await readdir(path.join(repoRoot, "docs"))).sort();
    assert.deepStrictEqual(docsEntries, ["README.md", ...categories], "docs/ holds more than the index and the four categories");

    // Every folder of documents, including nested ones such as reference/adr/, has a README that
    // indexes each document beside it and each sub-folder's README.
    const folders = (await listRepoFiles(/^docs\/.+\.md$/)).map((file) => path.dirname(file));
    for (const folder of new Set(folders)) {
      const entries = await readdir(path.join(repoRoot, folder), { withFileTypes: true });
      const index = await readFile(path.join(repoRoot, folder, "README.md"), "utf8");
      const targets = entries
        .filter((entry) => entry.isDirectory() || (entry.name.endsWith(".md") && entry.name !== "README.md"))
        .filter((entry) => !entry.isDirectory() || folders.includes(path.join(folder, entry.name)))
        .map((entry) => (entry.isDirectory() ? `${entry.name}/README.md` : entry.name));
      for (const target of targets) {
        assert.ok(index.includes(`(./${target})`), `${folder}/README.md does not index ${target}`);
      }
    }
  });

  it("HALL-2 AC6: ADRs are reference material, one file per ADR in docs/reference/adr/", async () => {
    const adrs = (await readdir(path.join(repoRoot, "docs/reference/adr"))).filter((name) => name !== "README.md");
    assert.ok(adrs.length > 0, "docs/reference/adr/ has no ADRs");
    for (const adr of adrs) assert.match(adr, /^\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$/, `${adr} is not NNNN-slug.md`);
    await assert.rejects(access(path.join(repoRoot, "docs/explanation/architecture-decisions.md")), /ENOENT/);
  });

  it("HALL-2 AC6: every internal Markdown link and anchor resolves", async () => {
    const broken = [];
    for (const file of await listRepoFiles(/\.md$/)) {
      const source = stripFences(await readFile(path.join(repoRoot, file), "utf8"));
      for (const [, target] of source.matchAll(/\]\(([^)\s]+)\)/g)) {
        if (/^[a-z]+:/i.test(target)) continue;
        const [targetPath, anchor] = target.split("#");
        const resolved = targetPath ? path.resolve(repoRoot, path.dirname(file), targetPath) : path.join(repoRoot, file);
        try {
          await access(resolved);
        } catch {
          broken.push(`${file} → ${target} (no such file)`);
          continue;
        }
        if (anchor && !headingAnchors(await readFile(resolved, "utf8")).has(anchor)) {
          broken.push(`${file} → ${target} (no such heading)`);
        }
      }
    }
    assert.deepStrictEqual(broken, [], "broken internal links");
  });

  it("HALL-2 AC1: CLAUDE.md replaces AGENTS.md and nothing refers to AGENTS.md", async () => {
    await assert.rejects(access(path.join(repoRoot, "AGENTS.md")), /ENOENT/, "AGENTS.md still exists");
    await access(path.join(repoRoot, "CLAUDE.md"));

    // This file has to name what it guards against, so it is the one exception.
    const thisFile = path.relative(repoRoot, import.meta.filename);
    for (const file of await listRepoFiles()) {
      if (file === thisFile) continue;
      const content = await readFile(path.join(repoRoot, file), "utf8");
      assert.ok(!content.includes("AGENTS.md"), `${file} refers to AGENTS.md`);
    }
  });

  it("HALL-2 AC8: no repo doc tells contributors to use conventional commits", async () => {
    for (const file of await listRepoFiles(/\.md$/)) {
      const content = await readFile(path.join(repoRoot, file), "utf8");
      assert.doesNotMatch(content, /conventional commits?/i, `${file} mentions conventional commits`);
    }
  });

  // Each script runs as a real child process, the way a contributor or CI would run it.
  for (const script of ["lint", "format:check"]) {
    it(`HALL-2 AC2: npm run ${script} runs and passes`, () => {
      const result = spawnSync("npm", ["run", "--silent", script], { cwd: repoRoot, encoding: "utf8" });
      assert.strictEqual(result.status, 0, `npm run ${script} failed:\n${result.stdout}${result.stderr}`);
    });
  }

  it("HALL-2 AC4: 2025 leftovers and the thonny script are gone", async () => {
    for (const leftover of [".ai", ".github/prompts", "lib/neopixel.py.esp32"]) {
      await assert.rejects(access(path.join(repoRoot, leftover)), /ENOENT/, `${leftover} still exists`);
    }
    const { scripts } = await readPackageJson();
    assert.strictEqual(scripts.thonny, undefined, "the thonny npm script is still defined");
  });

  it("HALL-2 AC5: LICENSE is MIT, matching the README's licence statement", async () => {
    const licence = await readFile(path.join(repoRoot, "LICENSE"), "utf8");
    assert.match(licence, /^MIT License\n/, "LICENSE is not the MIT licence");
    const readme = await readFile(path.join(repoRoot, "README.md"), "utf8");
    assert.match(readme, /licensed under the MIT Licence/, "README no longer states the MIT licence");
  });

  it("HALL-2 AC3: no ESLint or Prettier config files or packages remain", async () => {
    const rootFiles = await readdir(repoRoot);
    const configFiles = rootFiles.filter((name) => /^(\.?eslint|\.?prettier)/i.test(name));
    assert.deepStrictEqual(configFiles, [], "ESLint or Prettier config files remain");

    // The lockfile catches transitive leftovers that package.json alone would miss.
    const { devDependencies = {} } = await readPackageJson();
    const lockfile = await readFile(path.join(repoRoot, "package-lock.json"), "utf8");
    for (const tool of ["eslint", "prettier"]) {
      assert.ok(!Object.keys(devDependencies).some((name) => name.includes(tool)), `package.json still lists ${tool}`);
      assert.ok(!lockfile.includes(`node_modules/${tool}`), `package-lock.json still installs ${tool}`);
    }
  });
});
