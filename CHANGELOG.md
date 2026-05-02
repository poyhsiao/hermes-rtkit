# Changelog

## [0.1.0] - 2026-05-02

### Added
- Initial release
- `transform_terminal_output` hook integration with Hermes Agent
- RTK pipe-mode compression with auto-filter detection
- Support for cargo, pytest, git, npm, docker, kubectl, ruff, and more
- Fail-open design (RTK failures return original output)
- Configurable via `plugins.hermes-rtkit` in config.yaml
- `exclude_commands` configuration option
- `verbose` logging mode
- Full test suite with pytest
