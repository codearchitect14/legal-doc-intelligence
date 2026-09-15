from pathlib import Path
from uuid import UUID

from app.core.config import get_settings


def _document_dir(firm_id: UUID, case_id: UUID, document_id: UUID) -> Path:
    base = Path(get_settings().object_storage_path) / str(firm_id) / str(case_id) / str(document_id)
    base.mkdir(parents=True, exist_ok=True)
    return base


def save_upload(firm_id: UUID, case_id: UUID, document_id: UUID, filename: str, content: bytes) -> str:
    """Persist raw uploaded bytes to disk and return the stored file's path.

    Each document gets its own directory, and only the final path component
    of `filename` is used (`Path(filename).name`) - this is what neutralizes
    zip-slip when `filename` comes from an archive member (e.g.
    `../../etc/passwd`), since any directory traversal in it is discarded.
    """
    target_dir = _document_dir(firm_id, case_id, document_id)
    target_path = target_dir / Path(filename).name
    target_path.write_bytes(content)
    return str(target_path)
