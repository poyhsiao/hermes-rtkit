# hermes-rtkit

> RTK Integration for Hermes Agent -- compress terminal command outputs, save **60-90% tokens**

[![PyPI version](https://img.shields.io/pypi/v/hermes-rtkit.svg)](https://pypi.org/project/hermes-rtkit/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

## Overview

`hermes-rtkit` is a [Hermes Agent](https://github.com/nousresearch/hermes-agent) plugin that integrates [RTK (Rust Token Killer)](https://github.com/rtk-ai/rtk) to compress terminal command outputs before they reach the LLM context window.

When Hermes executes a terminal command (e.g., `cargo test`, `pytest`, `git diff`), the raw output can be thousands of tokens. `hermes-rtkit` pipes this output through RTK, which intelligently filters and compresses it -- preserving the signal while eliminating noise.

## Features

- **Transparent compression**: Integrates via Hermes's `transform_terminal_output` hook -- zero config needed for basic use
- **Auto-filter detection**: Automatically selects the right RTK filter based on the command (`cargo-test`, `pytest`, `git-diff`, etc.)
- **Fail-open design**: If RTK is unavailable or fails, original output is returned unchanged -- no broken pipelines
- **Configurable**: Disable per-command, use verbose logging, or point to a custom RTK path
- **Minimal dependencies**: Pure Python, no external runtime deps beyond RTK itself

## Installation

### RTK Requirement

First, install RTK:

```bash
# macOS
brew install rtk

# Linux
curl -fsSL https://rtk.ai/install.sh | sh
```

Verify:
```bash
rtk --version
```

### Hermes Plugin Installation

```bash
# Clone into Hermes plugins directory
git clone https://github.com/kimhsiao/hermes-rtkit ~/.hermes/plugins/hermes-rtkit
```

Enable in your Hermes config (`~/.hermes/config.yaml`):

```yaml
plugins:
  enabled:
    - hermes-rtkit

  hermes-rtkit:
    enabled: true           # master switch (default: true)
    verbose: false         # log compression events (default: false)
    rtk_path: "rtk"       # path to rtk binary (default: "rtk")
    exclude_commands:      # commands to never compress
      - git
      - cargo
```

Reload Hermes to activate the plugin.

## Usage

Once installed, compression happens automatically for supported commands:

| Command | RTK Filter |
|---------|-----------|
| `cargo test` / `cargo build` | `cargo-test` / `cargo-build` |
| `pytest` / `pytest tests/` | `pytest` |
| `git status` / `git diff` | `git-log` / `git-diff` |
| `npm run` / `pnpm` | `npm` / `pnpm` |
| `docker ps` / `docker images` | `docker` |
| `kubectl get` / `kubectl describe` | `kubectl` |
| `ruff check` / `ruff format` | `ruff` |

Full filter list: `rtk pipe --help`

## Configuration Reference

```yaml
plugins:
  hermes-rtkit:
    enabled: true              # Enable/disable all compression (default: true)
    verbose: false             # Print compression stats to stdout (default: false)
    rtk_path: "rtk"          # Path to RTK binary (default: "rtk")
    exclude_commands: []      # Base commands to skip, e.g. ["git", "cargo"]
```

## Architecture

```
Hermes executes command
        |
        v
terminal_tool.py runs command, gets raw output
        |
        v
invoke_hook("transform_terminal_output", command=, output=, ...)
        |
        v
hermes-rtkit hook registered by plugin.py
        |
        v
compression.py: is_supported_command() -> yes
        |
        v
subprocess.run(["rtk", "pipe", "-f", filter_name], input=output)
        |
        v
RTK compresses -> stdout returned
        |
        v
Original output replaced with compressed output
        |
        v
LLM sees compressed output (60-90% fewer tokens)
```

## Testing

```bash
pip install -e ".[dev]"
pytest
```

## License

Apache License 2.0 -- see [LICENSE](LICENSE)
