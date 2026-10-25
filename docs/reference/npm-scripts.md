# npm Scripts <!-- omit in toc -->

Every script in `package.json`, grouped by what it works on. Run each as `npm run <script>`; `npm test` runs `test`.

## Table of Contents <!-- omit in toc -->

- [1. Repo](#1-repo)
- [2. Python Host Tools](#2-python-host-tools)
- [3. Audio](#3-audio)
- [4. Pico](#4-pico)

## 1. Repo

| Script         | Runs                               | Purpose                                    |
| :------------- | :--------------------------------- | :----------------------------------------- |
| `test`         | `node --test "tests/**/*.test.js"` | Repo convention tests                      |
| `lint`         | `oxlint`                           | Lint JavaScript                            |
| `format`       | `oxfmt --write`                    | Format JavaScript, JSON, Markdown and TOML |
| `format:check` | `oxfmt --check`                    | Report formatting without writing          |

## 2. Python Host Tools

These need the virtual environment and `requirements-dev.txt`.

| Script      | Runs                 | Purpose                           |
| :---------- | :------------------- | :-------------------------------- |
| `lint:py`   | `ruff check devops/` | Lint host-side Python             |
| `format:py` | `black devops/`      | Format host-side Python           |
| `type:py`   | `mypy devops/`       | Type-check host-side Python       |
| `test:py`   | `pytest`             | Firmware tests with fake hardware |

## 3. Audio

| Script           | Runs                                | Purpose                                                                                           |
| :--------------- | :---------------------------------- | :------------------------------------------------------------------------------------------------ |
| `audio:prep`     | `devops/prepare_audio.py`           | Write numbered MP3s to `audio/prepared/`; see [Prepare Thunder Audio](../how-to/prepare-audio.md) |
| `audio:prep:dry` | `devops/prepare_audio.py --dry-run` | Preview the renaming                                                                              |

## 4. Pico

All use mpremote: over USB to the Pico, or over RFC 2217 to the Wokwi simulator.

| Script       | Runs                     | Purpose                                                                                                                        |
| :----------- | :----------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| `deploy`     | `devops/deploy.sh`       | Copy `src/` to the Pico; see [Deploy to the Pico](../how-to/deploy-to-pico.md)                                                 |
| `run`        | `devops/run.sh`          | Run `src/main.py` on the Pico without copying it                                                                               |
| `run:repl`   | `devops/run.sh --repl`   | Run, then drop into the REPL                                                                                                   |
| `serve`      | `devops/serve.sh`        | Mount `src/` on the Pico for live editing                                                                                      |
| `serve:stop` | `devops/serve.sh --stop` | Stop the mount                                                                                                                 |
| `simulate`   | `devops/simulate.sh`     | Copy `src/` into a running Wokwi simulation and start it in test mode; see [Simulate in Wokwi](../how-to/simulate-in-wokwi.md) |

[← Back to Reference](./README.md)
