import subprocess
import sys

from rich.console import Console

err_console = Console(stderr=True)


def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        return "libx265" in result.stdout or "libx265" in result.stderr
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_prerequisites() -> None:
    if not check_ffmpeg():
        err_console.print("[red]✖ ffmpeg with libx265 support not found[/]")
        err_console.print("  Install: sudo apt install ffmpeg (Ubuntu/Debian)")
        err_console.print("  Verify: ffmpeg -version | grep libx265")
        raise SystemExit(1)

    try:
        import typer  # noqa
        import rich  # noqa
    except ImportError:
        err_console.print("[red]✖ Missing Python dependencies[/]")
        err_console.print("  Install: pip install typer rich")
        raise SystemExit(1)
