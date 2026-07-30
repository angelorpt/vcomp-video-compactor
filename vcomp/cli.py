import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table

from . import VERSION
from .compressor import check_ffmpeg, compress_videos
from .models import CompressionReport, CompressionResult, OutputMode, VideoFile
from .scanner import DEFAULT_EXTENSIONS, scan_directory

app = typer.Typer(
    name="vcomp",
    help="Video compactor — compress video courses with ffmpeg + libx265",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)


def _check_prerequisites():
    if not check_ffmpeg():
        err_console.print("[red]✖ ffmpeg with libx265 support not found[/]")
        err_console.print("  Install: sudo apt install ffmpeg (Ubuntu/Debian)")
        err_console.print("  Verify: ffmpeg -version | grep libx265")
        raise typer.Exit(code=1)

    try:
        import typer as _  # noqa
        import rich as _  # noqa
    except ImportError:
        err_console.print("[red]✖ Missing Python dependencies[/]")
        err_console.print("  Install: pip install typer rich")
        raise typer.Exit(code=1)


def _build_output_path(video: VideoFile, input_dir: Path, output_dir: Optional[Path], mode: OutputMode) -> Path:
    if mode == OutputMode.SEPARATE:
        assert output_dir is not None, "--output-dir required for separate mode"
        rel = video.path.relative_to(input_dir.resolve())
        return (output_dir.resolve() / rel).with_suffix(video.path.suffix)

    parent = video.path.parent
    stem = video.path.stem
    ext = video.path.suffix
    return parent / f"{stem}_compactado{ext}"


def _format_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} PB"


@app.command()
def run(
    directory: Path = typer.Argument(..., help="Directory containing video files", exists=True, file_okay=False, resolve_path=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan subdirectories recursively"),
    mode: OutputMode = typer.Option(OutputMode.SAME, "--mode", "-m", help="Output mode"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory (required for 'separate' mode)", exists=False, resolve_path=True),
    crf: int = typer.Option(28, "--crf", help="CRF value for x265 (0-51, lower = better quality)"),
    preset: str = typer.Option("medium", "--preset", help="x265 preset: ultrafast, fast, medium, slow, veryslow"),
    audio_bitrate: str = typer.Option("128k", "--audio-bitrate", help="Audio bitrate (e.g. 96k, 128k, 192k)"),
    extensions: str = typer.Option(",".join(DEFAULT_EXTENSIONS), "--extensions", help="Comma-separated video extensions"),
    jobs: int = typer.Option(os.cpu_count() or 2, "--jobs", "-j", help="Number of parallel compression jobs"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Re-compress existing files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without compressing"),
):
    _check_prerequisites()

    ext_set = {f".{e.strip().lstrip('.')}" for e in extensions.split(",")}
    console.print(f"[bold]Scanning:[/] [cyan]{directory}[/]")
    if recursive:
        console.print("  Mode: [cyan]recursive[/]")
    else:
        console.print("  Mode: [cyan]non-recursive[/]")

    videos = scan_directory(directory, recursive=recursive, extensions=ext_set)
    if not videos:
        console.print("[yellow]No video files found[/]")
        raise typer.Exit()

    console.print(f"  Found: [bold]{len(videos)}[/] video files ({_format_size(sum(v.size_bytes for v in videos))})")

    total_input = sum(v.size_bytes for v in videos)

    if dry_run:
        table = Table(title="Dry Run — Files to Compress")
        table.add_column("File", style="cyan")
        table.add_column("Size", style="white")
        table.add_column("Output", style="green")
        for v in videos:
            out = _build_output_path(v, directory, output_dir, mode)
            table.add_row(str(v.path), _format_size(v.size_bytes), str(out))
        table.add_row("[bold]Total[/]", _format_size(total_input), f"[bold]{len(videos)} files[/]")
        console.print(table)
        raise typer.Exit()

    report = CompressionReport()

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
    )

    task_id = progress.add_task("[cyan]Compressing...", total=len(videos))

    def on_progress(result: CompressionResult):
        if result.success:
            report.results.append(result)
            desc = f"[green]✓[/] {result.output_path.name} ({_format_size(result.output_size)})"
        elif result.error == "Skipped (already exists)":
            report.total_skipped += 1
            desc = f"[yellow]⏭[/] {result.output_path.name} (skipped)"
        else:
            report.total_errors += 1
            desc = f"[red]✖[/] {result.output_path.name}: {result.error}"
        progress.update(task_id, advance=1, description=desc)

    try:
        with progress:
            compress_videos(
                videos=videos,
                crf=crf,
                preset=preset,
                audio_bitrate=audio_bitrate,
                mode=mode,
                input_dir=directory,
                output_dir=output_dir,
                jobs=jobs,
                overwrite=overwrite,
                progress_callback=on_progress,
            )

        table = Table(title="Compression Summary", show_header=True)
        table.add_column("Metric", style="bold")
        table.add_column("Value")
        table.add_row("Total files", str(len(videos)))
        table.add_row("Compressed", str(len(report.successful)))
        table.add_row("Skipped", str(report.total_skipped))
        table.add_row("Errors", f"[red]{report.total_errors}[/]" if report.total_errors else "0")
        table.add_row("Input size", _format_size(report.total_input_size))
        table.add_row("Output size", _format_size(report.total_output_size))
        table.add_row("Space saved", f"[green]{_format_size(report.total_saved)}[/] ({(report.total_saved / report.total_input_size * 100):.1f}%)" if report.total_input_size else "0")
        console.print(table)

    except KeyboardInterrupt:
        err_console.print("\n[yellow]Interrupted by user[/]")


@app.command()
def clean(
    directory: Path = typer.Argument(".", help="Directory to clean backups from", exists=True, file_okay=False, resolve_path=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Find .originais/ recursively"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without deleting"),
):
    backup_dirs: List[Path] = []
    if recursive:
        for root, dirs, _files in os.walk(str(directory)):
            if ".originais" in dirs:
                backup_dirs.append(Path(root) / ".originais")
    else:
        candidate = directory / ".originais"
        if candidate.is_dir():
            backup_dirs.append(candidate)

    if not backup_dirs:
        console.print("[yellow]No .originais/ directories found[/]")
        raise typer.Exit()

    total_size = 0
    table = Table(title="Backup Directories Found")
    table.add_column("Path", style="cyan")
    table.add_column("Size", style="white")
    for d in backup_dirs:
        dir_size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        total_size += dir_size
        table.add_row(str(d), _format_size(dir_size))
    table.add_row("[bold]Total[/]", _format_size(total_size))
    console.print(table)

    if dry_run:
        console.print("[yellow]Dry run — no files deleted[/]")
        raise typer.Exit()

    confirm = typer.confirm(f"Delete {len(backup_dirs)} backup director{'y' if len(backup_dirs) == 1 else 'ies'} ({_format_size(total_size)})?")
    if not confirm:
        console.print("[yellow]Cancelled[/]")
        raise typer.Exit()

    deleted = 0
    errors = 0
    for d in backup_dirs:
        try:
            for f in d.rglob("*"):
                if f.is_file():
                    f.unlink()
            for p in sorted(d.rglob("*"), key=lambda x: len(str(x)), reverse=True):
                if p.is_dir():
                    p.rmdir()
            d.rmdir()
            deleted += 1
            console.print(f"[green]✓[/] Removed {d}")
        except OSError as e:
            err_console.print(f"[red]✖[/] Error deleting {d}: {e}")
            errors += 1

    console.print(f"[bold]Done:[/] {deleted} directories removed, {errors} errors")


@app.command()
def install(
    home: bool = typer.Option(False, "--home", "-H", help="Install to ~/.local/bin instead of detecting pip"),
):
    _check_prerequisites()

    if home:
        bin_dir = Path.home() / ".local" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        script_path = bin_dir / "vcomp"
        script_content = f'''#!/usr/bin/env python3
import sys
sys.path.insert(0, {str(Path(sys.argv[0]).resolve().parent.parent)!r})
from vcomp.cli import app
app()
'''
        script_path.write_text(script_content)
        script_path.chmod(0o755)
        console.print(f"[green]✓[/] Installed to {script_path}")
        console.print(f"  Ensure {bin_dir} is in your PATH")
    else:
        console.print("Installing via pip...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "-e", "."], capture_output=True, text=True)
        if result.returncode == 0:
            console.print("[green]✓[/] Installed via pip")
        else:
            err_console.print(f"[red]✖[/] pip install failed:\n{result.stderr}")
            raise typer.Exit(code=1)


@app.callback()
def main():
    pass


def _entry_point():
    app()


if __name__ == "__main__":
    app()
