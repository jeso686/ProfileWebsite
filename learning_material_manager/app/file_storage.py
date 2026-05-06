from __future__ import annotations

import mimetypes
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATERIALS_DIR = PROJECT_ROOT / "storage" / "materials"


def ensure_storage_path() -> None:
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)


def clean_input_path(file_path: str) -> str:
    return file_path.strip().strip('"').strip("'")


def file_exists(file_path: str) -> bool:
    return Path(clean_input_path(file_path)).expanduser().is_file()


def get_unique_target_path(filename: str) -> Path:
    ensure_storage_path()
    safe_name = Path(clean_input_path(filename)).name
    if not safe_name:
        safe_name = "material.txt"
    if "." not in safe_name:
        safe_name = f"{safe_name}.txt"

    target_path = MATERIALS_DIR / safe_name
    original_stem = target_path.stem
    original_suffix = target_path.suffix
    counter = 1
    while target_path.exists():
        target_path = MATERIALS_DIR / f"{original_stem}_{counter}{original_suffix}"
        counter += 1
    return target_path


def get_metadata(target_path: Path) -> dict[str, str | int]:
    mime_type, _ = mimetypes.guess_type(target_path.name)
    file_type = mime_type or (target_path.suffix.replace(".", "") or "unknown")

    return {
        "filename": target_path.name,
        "file_type": file_type,
        "file_size": target_path.stat().st_size,
        "file_path": str(target_path.relative_to(PROJECT_ROOT)),
    }


def copy_material_to_storage(source_file_path: str) -> dict[str, str | int]:
    source_path = Path(clean_input_path(source_file_path)).expanduser().resolve()
    target_path = get_unique_target_path(source_path.name)
    shutil.copy2(source_path, target_path)
    return get_metadata(target_path)


def create_material_file(filename: str, content: str) -> dict[str, str | int]:
    target_path = get_unique_target_path(filename)
    target_path.write_text(content, encoding="utf-8")
    return get_metadata(target_path)


def resolve_material_path(file_path: str) -> Path:
    stored_path = Path(clean_input_path(file_path)).expanduser()
    if stored_path.is_absolute():
        return stored_path
    return PROJECT_ROOT / stored_path
