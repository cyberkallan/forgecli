"""In-app file manager for generated projects."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import List, Optional

import questionary
from rich.console import Console
from rich.table import Table

from .core.logging_utils import get_logger

_LOG = get_logger("filemanager")

ACTIONS = ["Open", "Preview", "Edit", "Rename", "Duplicate", "Move",
           "Delete", "Search", "Sort", "Back"]


def list_files(root: Path, *, sort_by: str = "name") -> List[Path]:
    files = sorted(p for p in root.rglob("*") if p.is_file()
                   and "__pycache__" not in p.parts)
    if sort_by == "name":
        files.sort(key=lambda p: str(p.relative_to(root)).lower())
    elif sort_by == "size":
        files.sort(key=lambda p: p.stat().st_size, reverse=True)
    elif sort_by == "modified":
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def manage(project_root: Path, console: Console, theme) -> None:
    """Run the interactive file manager loop for ``project_root``."""
    root = Path(project_root)
    sort_by = "name"
    while True:
        files = list_files(root, sort_by=sort_by)
        console.print(_files_table(files, root, theme))
        action = questionary.select("File manager action", choices=ACTIONS).ask()
        if not action or action == "Back":
            return

        if action == "Sort":
            sort_by = questionary.select(
                "Sort by", ["name", "size", "modified"], default=sort_by).ask() or sort_by
            continue

        if action == "Search":
            query = questionary.text("Search substring").ask() or ""
            matches = [p for p in files if query.lower() in p.name.lower()]
            console.print(_files_table(matches, root, theme))
            continue

        rel = questionary.select(
            "Select file", choices=[str(p.relative_to(root)) for p in files]
        ).ask()
        if not rel:
            continue
        target = root / rel

        if action == "Open":
            _open_in_editor(target)
        elif action == "Preview":
            _preview(target, console, theme)
        elif action == "Edit":
            _open_in_editor(target)
        elif action == "Rename":
            _rename(target, console, theme)
        elif action == "Duplicate":
            _duplicate(target, console, theme)
        elif action == "Move":
            _move(target, root, console, theme)
        elif action == "Delete":
            _delete(target, console, theme)


def _files_table(files: List[Path], root: Path, theme) -> Table:
    table = Table(header_style=f"bold {theme.secondary}", border_style=theme.border)
    table.add_column("Path")
    table.add_column("Size", justify="right")
    table.add_column("Modified")
    for fp in files:
        rel = str(fp.relative_to(root))
        size = fp.stat().st_size
        mtime = os.path.getmtime(fp)
        import datetime as _dt
        when = _dt.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        table.add_row(rel, _human_size(size), when)
    return table


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _open_in_editor(path: Path) -> None:
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        os.system(f"{editor} {path}")
    else:
        print(path.read_text(encoding="utf-8", errors="replace"))


def _preview(path: Path, console: Console, theme) -> None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        console.print(f"[{theme.danger}]Read failed: {exc}[/]")
        return
    console.print(text[:4000])
    if len(text) > 4000:
        console.print(f"[{theme.muted}](truncated, {len(text)} total bytes)[/]")


def _rename(path: Path, console: Console, theme) -> None:
    new_name = questionary.text("New name", default=path.name).ask()
    if not new_name or new_name == path.name:
        return
    target = path.with_name(new_name)
    try:
        path.rename(target)
        console.print(f"[{theme.success}]Renamed to {target}[/]")
    except OSError as exc:
        console.print(f"[{theme.danger}]Rename failed: {exc}[/]")


def _duplicate(path: Path, console: Console, theme) -> None:
    dest = path.with_name(path.stem + "_copy" + path.suffix)
    try:
        shutil.copy2(path, dest)
        console.print(f"[{theme.success}]Duplicated to {dest}[/]")
    except OSError as exc:
        console.print(f"[{theme.danger}]Duplicate failed: {exc}[/]")


def _move(path: Path, root: Path, console: Console, theme) -> None:
    dest_rel = questionary.text("Destination (relative to project root)",
                                default="assets/").ask()
    if not dest_rel:
        return
    dest_dir = root / dest_rel
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    try:
        shutil.move(str(path), str(dest))
        console.print(f"[{theme.success}]Moved to {dest}[/]")
    except OSError as exc:
        console.print(f"[{theme.danger}]Move failed: {exc}[/]")


def _delete(path: Path, console: Console, theme) -> None:
    if not questionary.confirm(f"Delete {path.name}?", default=False).ask():
        return
    try:
        path.unlink()
        console.print(f"[{theme.warning}]Deleted {path.name}[/]")
    except OSError as exc:
        console.print(f"[{theme.danger}]Delete failed: {exc}[/]")


__all__ = ["manage", "list_files", "ACTIONS"]