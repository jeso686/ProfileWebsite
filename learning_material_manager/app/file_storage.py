from __future__ import annotations

import mimetypes
import shutil
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MATERIALS_DIR = PROJECT_ROOT / "storage" / "materials"


def ensure_storage_path() -> None:
    MATERIALS_DIR.mkdir(parents=True, exist_ok=True)


def file_exists(file_path: str) -> bool:
    return Path(file_path).is_file()


def copy_material_to_storage(source_file_path: str) -> dict[str, str | int]:
    ensure_storage_path()
    source_path = Path(source_file_path).resolve()
    target_path = MATERIALS_DIR / source_path.name

    counter = 1
    while target_path.exists():
        target_path = MATERIALS_DIR / f"{source_path.stem}_{counter}{source_path.suffix}"
        counter += 1

    shutil.copy2(source_path, target_path)

    mime_type, _ = mimetypes.guess_type(target_path.name)
    file_type = mime_type or (target_path.suffix.replace(".", "") or "unknown")

    return {
        "filename": target_path.name,
        "file_type": file_type,
        "file_size": target_path.stat().st_size,
        "file_path": str(target_path),
    }
