from __future__ import annotations

import base64
import mimetypes
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings

TEXT_EXTENSIONS = {".html", ".htm", ".txt", ".json", ".xml", ".log"}
SUBMISSION_PROOF_PREFIX = "submission-proofs"
ALLOWED_SUBMISSION_UPLOAD_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
}


@dataclass
class AssetPreview:
    asset_path: str
    content_type: str
    kind: str
    file_name: str
    byte_size: int
    truncated: bool
    text_content: str | None = None
    base64_content: str | None = None


@dataclass
class StoredSubmissionUpload:
    asset_path: str
    content_type: str
    file_name: str
    byte_size: int


def _resolve_root(configured_root: str) -> Path:
    root = Path(configured_root)
    if not root.is_absolute():
        root = Path.cwd() / root
    root.mkdir(parents=True, exist_ok=True)
    return root.resolve()


def get_artifact_root() -> Path:
    settings = get_settings()
    return _resolve_root(settings.artifact_storage_root)


def get_submission_upload_root() -> Path:
    settings = get_settings()
    return _resolve_root(settings.submission_upload_root)


def write_scrape_html_snapshot(*, source_name: str, run_id: int, html: str) -> str:
    root = get_artifact_root()
    target = root / "scrape-errors" / source_name / f"run-{run_id}-snapshot.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target.relative_to(root).as_posix()


def write_submission_upload(
    *, file_name: str, content_type: str, data: bytes
) -> StoredSubmissionUpload:
    if content_type not in ALLOWED_SUBMISSION_UPLOAD_CONTENT_TYPES:
        raise ValueError("Unsupported submission proof content type")

    extension = (
        Path(file_name).suffix.lower() or ALLOWED_SUBMISSION_UPLOAD_CONTENT_TYPES[content_type]
    )
    if extension not in ALLOWED_SUBMISSION_UPLOAD_CONTENT_TYPES.values():
        extension = ALLOWED_SUBMISSION_UPLOAD_CONTENT_TYPES[content_type]

    timestamp = datetime.now(UTC)
    root = get_submission_upload_root()
    relative_path = (
        Path(SUBMISSION_PROOF_PREFIX)
        / f"{timestamp.year:04d}"
        / f"{timestamp.month:02d}"
        / f"{uuid4().hex}{extension}"
    )
    target = root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return StoredSubmissionUpload(
        asset_path=relative_path.as_posix(),
        content_type=content_type,
        file_name=target.name,
        byte_size=len(data),
    )


def is_local_submission_asset_path(asset_path: str) -> bool:
    return asset_path.startswith(f"{SUBMISSION_PROOF_PREFIX}/")


def resolve_artifact_path(asset_path: str) -> Path:
    root = (
        get_submission_upload_root()
        if is_local_submission_asset_path(asset_path)
        else get_artifact_root()
    )
    candidate = Path(asset_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if root != resolved and root not in resolved.parents:
        raise ValueError("Asset path is outside the configured artifact root")
    if not resolved.exists() or not resolved.is_file():
        raise FileNotFoundError("Asset file not found")
    return resolved


def build_asset_preview(asset_path: str) -> AssetPreview:
    settings = get_settings()
    resolved = resolve_artifact_path(asset_path)
    data = resolved.read_bytes()
    content_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
    limit = max(settings.asset_preview_max_bytes, 1024)
    byte_size = len(data)
    truncated = byte_size > limit
    preview_data = data[:limit]

    if content_type.startswith("image/"):
        return AssetPreview(
            asset_path=asset_path,
            content_type=content_type,
            kind="image",
            file_name=resolved.name,
            byte_size=byte_size,
            truncated=truncated,
            base64_content=base64.b64encode(preview_data).decode("ascii"),
        )

    if content_type.startswith("text/") or resolved.suffix.lower() in TEXT_EXTENSIONS:
        return AssetPreview(
            asset_path=asset_path,
            content_type=content_type,
            kind="text",
            file_name=resolved.name,
            byte_size=byte_size,
            truncated=truncated,
            text_content=preview_data.decode("utf-8", errors="replace"),
        )

    return AssetPreview(
        asset_path=asset_path,
        content_type=content_type,
        kind="binary",
        file_name=resolved.name,
        byte_size=byte_size,
        truncated=truncated,
    )
