import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table

from .compressor import compress_videos
from .models import CompressionReport, CompressionResult, OutputMode, VideoFile
from .path_resolver import build_output_path
from .prerequisite_checker import check_prerequisites
from .scanner import DEFAULT_EXTENSIONS, scan_directory

app = typer.Typer(
    name="vcomp",
    help="Video compactor — compress video with ffmpeg + libx265",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)


def _format_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} PB"


def _build_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
        console=console,
    )


def _build_summary_table(videos: List[VideoFile], report: CompressionReport) -> Table:
    table = Table(title="Compression Summary", show_header=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Total files", str(len(videos)))
    table.add_row("Compressed", str(len(report.successful)))
    table.add_row("Skipped", str(report.total_skipped))
    table.add_row("Errors", f"[red]{report.total_errors}[/]" if report.total_errors else "0")
    table.add_row("Input size", _format_size(report.total_input_size))
    table.add_row("Output size", _format_size(report.total_output_size))
    if report.total_input_size:
        pct = (report.total_saved / report.total_input_size * 100)
        table.add_row("Space saved", f"[green]{_format_size(report.total_saved)}[/] ({pct:.1f}%)")
    else:
        table.add_row("Space saved", "0")
    return table


def _find_originals(directory: Path, recursive: bool) -> List[Path]:
    result: List[Path] = []
    if recursive:
        for root, dirs, _files in os.walk(str(directory)):
            if "_originals" in dirs:
                result.append(Path(root) / "_originals")
    else:
        candidate = directory / "_originals"
        if candidate.is_dir():
            result.append(candidate)
    return result


def _find_logs(directory: Path, recursive: bool) -> List[Path]:
    result: List[Path] = []
    for root, _dirs, files in os.walk(str(directory)):
        for f in files:
            if f == "vcomp-log.json":
                result.append(Path(root) / f)
        if not recursive:
            break
    return result


def _confirm_action(items: List[Path], item_name: str, dry_run: bool) -> bool:
    if not items:
        console.print(f"[yellow]No {item_name} found[/]")
        return False

    total_size = 0
    table = Table(title=f"{item_name.title()} Found")
    table.add_column("Path", style="cyan")
    table.add_column("Size", style="white")
    for d in items:
        dir_size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) if d.is_dir() else 0
        total_size += dir_size
        table.add_row(str(d), _format_size(dir_size))
    table.add_row("[bold]Total[/]", _format_size(total_size))
    console.print(table)

    if dry_run:
        console.print("[yellow]Dry run — nothing executed[/]")
        return False

    label = item_name.rstrip("s")
    confirm = typer.confirm(f"Delete {len(items)} {label}{'s' if len(items) != 1 else ''} ({_format_size(total_size)})?")
    if not confirm:
        console.print("[yellow]Cancelled[/]")
        return False
    return True


@app.command()
def run(
    directory: Path = typer.Argument(..., help="Directory containing video files", exists=True, file_okay=False, resolve_path=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Scan subdirectories recursively"),
    mode: OutputMode = typer.Option(OutputMode.KEEP, "--mode", "-m", help="Output mode: keep (default), replace, clone"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", "-o", help="Output directory (required for 'clone' mode)", exists=False, resolve_path=True),
    crf: int = typer.Option(28, "--crf", help="CRF value for x265 (0-51, lower = better quality)"),
    preset: str = typer.Option("medium", "--preset", help="x265 preset: ultrafast, fast, medium, slow, veryslow"),
    audio_bitrate: str = typer.Option("128k", "--audio-bitrate", help="Audio bitrate (e.g. 96k, 128k, 192k)"),
    extensions: str = typer.Option(",".join(DEFAULT_EXTENSIONS), "--extensions", help="Comma-separated video extensions"),
    jobs: int = typer.Option(os.cpu_count() or 2, "--jobs", "-j", help="Number of parallel compression jobs"),
    overwrite: bool = typer.Option(False, "--overwrite", help="Re-compress existing files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without compressing"),
):
    check_prerequisites()

    ext_set = {f".{e.strip().lstrip('.')}" for e in extensions.split(",")}
    console.print(f"[bold]Scanning:[/] [cyan]{directory}[/]")
    console.print(f"  Mode: [cyan]{'recursive' if recursive else 'non-recursive'}[/]")

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
            out = build_output_path(v, directory, output_dir, mode)
            table.add_row(str(v.path), _format_size(v.size_bytes), str(out))
        table.add_row("[bold]Total[/]", _format_size(total_input), f"[bold]{len(videos)} files[/]")
        console.print(table)
        raise typer.Exit()

    report = CompressionReport()
    progress = _build_progress()
    task_id = progress.add_task("[cyan]Compressing...", total=len(videos))
    log_path = directory / "vcomp-log.json"

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
            results = compress_videos(
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
                log_path=log_path,
            )
        console.print(_build_summary_table(videos, report))

    except KeyboardInterrupt:
        err_console.print("\n[yellow]Interrupted by user[/]")


@app.command()
def clean(
    directory: Path = typer.Argument(".", help="Directory to clean", exists=True, file_okay=False, resolve_path=True),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Find _originals/ recursively"),
    logs: bool = typer.Option(False, "--logs", "-l", help="Remove only vcomp-log.json files"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without deleting"),
):
    if logs:
        items = _find_logs(directory, recursive)
        if not _confirm_action(items, "log files", dry_run):
            raise typer.Exit()
        deleted = 0
        errors = 0
        for f in items:
            try:
                f.unlink()
                console.print(f"[green]✓[/] Removed {f}")
                deleted += 1
            except OSError as e:
                err_console.print(f"[red]✖[/] Error deleting {f}: {e}")
                errors += 1
        console.print(f"[bold]Done:[/] {deleted} log files removed, {errors} errors")
        return

    items = _find_originals(directory, recursive)
    if not _confirm_action(items, "_originals directories", dry_run):
        raise typer.Exit()

    deleted = 0
    errors = 0
    for d in items:
        try:
            shutil.rmtree(d)
            deleted += 1
            console.print(f"[green]✓[/] Removed {d}")
        except OSError as e:
            err_console.print(f"[red]✖[/] Error deleting {d}: {e}")
            errors += 1

    console.print(f"[bold]Done:[/] {deleted} directories removed, {errors} errors")


@app.command()
def rollback(
    directory: Path = typer.Argument(".", help="Directory to rollback", exists=True, file_okay=False, resolve_path=True),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be restored without executing"),
):
    items = _find_originals(directory, recursive=True)
    if not items:
        console.print("[yellow]No _originals/ directories found[/]")
        raise typer.Exit()

    total_files = 0
    table = Table(title="Rollback — Files to Restore")
    table.add_column("Original", style="cyan")
    table.add_column("Backup", style="white")
    table.add_column("Size", style="white")
    for d in items:
        parent = d.parent
        for f in d.iterdir():
            if f.is_file():
                total_files += 1
                table.add_row(str(parent / f.name), str(f), _format_size(f.stat().st_size))
    console.print(table)

    if dry_run:
        console.print(f"[yellow]Dry run — {total_files} files would be restored, {len(items)} _originals/ removed[/]")
        raise typer.Exit()

    confirm = typer.confirm(f"Restore {total_files} file(s) and remove {len(items)} _originals/ director{'y' if len(items) == 1 else 'ies'}?")
    if not confirm:
        console.print("[yellow]Cancelled[/]")
        raise typer.Exit()

    restored = 0
    errors = 0
    for d in items:
        parent = d.parent
        for f in d.iterdir():
            if f.is_file():
                try:
                    shutil.move(str(f), str(parent / f.name))
                    restored += 1
                except OSError as e:
                    err_console.print(f"[red]✖[/] Error restoring {f}: {e}")
                    errors += 1
    for d in items:
        try:
            shutil.rmtree(d)
        except OSError as e:
            err_console.print(f"[red]✖[/] Error removing {d}: {e}")
            errors += 1

    log_files = _find_logs(directory, recursive=True)
    for f in log_files:
        try:
            f.unlink()
        except OSError:
            pass

    console.print(f"[bold]Done:[/] {restored} files restored, {errors} errors")


@app.command()
def install(
    home: bool = typer.Option(False, "--home", "-H", help="Install to ~/.local/bin instead of detecting pip"),
):
    check_prerequisites()

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
