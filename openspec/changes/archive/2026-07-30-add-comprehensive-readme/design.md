## Context

Single-file documentation change. Existing project is fully implemented and tested — README.md does not exist yet. Project has pyproject.toml, AGENTS.md, and source code with Typer CLI and Rich UI.

## Goals / Non-Goals

**Goals:**
- Create a professional README.md covering motivation, features, installation, usage, output modes, compression tips, architecture

**Non-Goals:**
- No changes to code, dependencies, or project structure

## Decisions

- Single markdown file at project root (standard convention)
- Badges from shields.io for Python, license, ffmpeg, Typer, Rich
- Usage examples use `vcomp` directly (assumes installed via pip or --home)
- Compression tips table references the existing spec documentation

## Risks / Trade-offs

- README can become stale if code changes without updating it — mitigated by keeping it concise and pointing to --help for detailed reference
