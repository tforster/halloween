# Set Up the Development Environment <!-- omit in toc -->

Prepare a host machine (Linux, WSL2 or ChromeOS Linux) to work on the project: Node.js for repo tooling, a Python virtual environment for the host-side tools and mpremote for talking to the Pico.

## Table of Contents <!-- omit in toc -->

- [1. Prerequisites](#1-prerequisites)
- [2. Steps](#2-steps)
  - [2.1. Clone the repository and install Node.js tooling](#21-clone-the-repository-and-install-nodejs-tooling)
  - [2.2. Create the Python virtual environment](#22-create-the-python-virtual-environment)
  - [2.3. Install ffmpeg and Graphviz](#23-install-ffmpeg-and-graphviz)
- [3. Verification](#3-verification)

## 1. Prerequisites

- Python 3.13 or later
- Node.js (latest LTS)
- Git or jj
- VS Code, with the Markdown All in One extension (`yzhang.markdown-all-in-one`)
- ffmpeg, which `devops/prepare_audio.py` uses to convert WAV files
- Graphviz, which WireViz uses to render the [wiring diagram](../reference/assets/wiring.yml) (`npm run wiring` and its pytest check)

> [!NOTE]
>
> Graphviz is a new host dependency in 2026, added with the WireViz wiring harness ([ADR-012](../reference/adr/0012-wireviz-and-wokwi.md)). Without it, `npm run wiring` fails and `npm run test:py` fails its wiring render test.

## 2. Steps

### 2.1. Clone the repository and install Node.js tooling

```bash
git clone https://github.com/tforster/halloween.git
cd halloween
npm install
```

`npm install` brings in oxlint and oxfmt. See [npm Scripts](../reference/npm-scripts.md) for what each script runs.

### 2.2. Create the Python virtual environment

```bash
python3.13 -m venv venv
source activate.sh
pip install -r requirements.txt       # mpremote, pyserial, pydub
pip install -r requirements-dev.txt   # ruff, black, mypy, pytest, wireviz
```

### 2.3. Install ffmpeg and Graphviz

ffmpeg prepares the thunder audio; Graphviz renders the wiring diagram for `npm run wiring` and its test.

```bash
sudo apt install ffmpeg graphviz   # Debian, Ubuntu, WSL2
brew install ffmpeg graphviz       # macOS
```

## 3. Verification

```bash
npm test          # repo convention tests
mpremote --help   # mpremote is on the PATH inside the venv
```

Connect the Pico 2 by USB, then continue with [Deploy to the Pico](./deploy-to-pico.md).

[← Back to How-To Guides](./README.md)
