# Add a DevOps Script <!-- omit in toc -->

Add a host-side helper to `devops/` so it fits the existing tooling.

## Table of Contents <!-- omit in toc -->

- [1. Steps](#1-steps)
- [2. Verification](#2-verification)

## 1. Steps

1. Put the script in `devops/`. Shell scripts source `devops/includes/parseArgs.sh` for argument parsing and carry a usage header like `devops/run.sh`.
2. Python scripts start with `#!/usr/bin/env python3`, a module docstring with usage examples and type hints throughout.
3. Use British/Canadian spelling in comments and output.
4. Add an npm script to `package.json` so it runs as `npm run <name>`.
5. Add the script to [npm Scripts](../reference/npm-scripts.md).

## 2. Verification

`npm run <name> -- --help` prints the usage, and `npm run lint:py` passes for Python scripts.

[← Back to How-To Guides](./README.md)
