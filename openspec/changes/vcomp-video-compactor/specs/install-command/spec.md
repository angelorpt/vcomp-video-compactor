# Install Command

## Capability

Self-install mechanism to make the `vcomp` command available system-wide.

## Requirements

### REQ-IC-01: Install subcommand
- `vcomp install` MUST install the tool to `~/.local/bin/vcomp`
- The installed script MUST be a standalone Python entry point that runs the tool

### REQ-IC-02: Prerequisite check
- MUST verify `ffmpeg` is installed and supports `libx265`
- MUST verify required Python packages (`typer`, `rich`) are available
- If prerequisites are missing, MUST display clear installation commands

### REQ-IC-03: Install via pip
- `pyproject.toml` MUST define a console script entry point `vcomp = vcomp.cli:app`
- `pip install --user .` or `pip install -e .` MUST work as an alternative install method
