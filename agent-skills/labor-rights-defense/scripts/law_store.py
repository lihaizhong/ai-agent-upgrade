from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

try:
    from .law_parser import parse_law_html
except ImportError:  # pragma: no cover
    from law_parser import parse_law_html


@dataclass(frozen=True)
class StoredLawVersion:
    doc_id: str
    source_url: str
    retrieved_at: str
    content_hash: str
    raw_html_path: str
    parsed_json_path: str


def _timestamp() -> str:
    return datetime.now().astimezone().isoformat()


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _doc_dir(cache_law_dir: Path, doc_id: str) -> Path:
    return cache_law_dir / doc_id


def _index_path(doc_dir: Path) -> Path:
    return doc_dir / "index.json"


def load_index(doc_dir: Path) -> dict:
    path = _index_path(doc_dir)
    if not path.exists():
        return {"doc_id": doc_dir.name, "versions": [], "updated_at": None}
    return json.loads(path.read_text(encoding="utf-8"))


def save_index(doc_dir: Path, index: dict) -> None:
    index["updated_at"] = _timestamp()
    _index_path(doc_dir).write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def store_law_html(
    *,
    cache_law_dir: Path,
    doc_id: str,
    source_url: str,
    retrieved_at: str,
    content_hash: str,
    html: str,
) -> StoredLawVersion:
    doc_dir = _doc_dir(cache_law_dir, doc_id)
    _ensure_dir(doc_dir)

    index = load_index(doc_dir)
    for item in index.get("versions", []):
        if item.get("content_hash") == content_hash:
            # Already stored.
            return StoredLawVersion(
                doc_id=doc_id,
                source_url=item.get("source_url", source_url),
                retrieved_at=item.get("retrieved_at", retrieved_at),
                content_hash=content_hash,
                raw_html_path=item["raw_html_path"],
                parsed_json_path=item["parsed_json_path"],
            )

    version_dir = doc_dir / content_hash
    _ensure_dir(version_dir)
    raw_path = version_dir / "raw.html"
    parsed_path = version_dir / "parsed.json"

    raw_path.write_text(html, encoding="utf-8")
    parsed_payload = parse_law_html(html)
    parsed_payload.update(
        {
            "doc_id": doc_id,
            "source_url": source_url,
            "retrieved_at": retrieved_at,
            "content_hash": content_hash,
        }
    )
    parsed_path.write_text(
        json.dumps(parsed_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    index.setdefault("versions", []).append(
        {
            "source_url": source_url,
            "retrieved_at": retrieved_at,
            "content_hash": content_hash,
            "raw_html_path": str(raw_path),
            "parsed_json_path": str(parsed_path),
        }
    )
    save_index(doc_dir, index)

    return StoredLawVersion(
        doc_id=doc_id,
        source_url=source_url,
        retrieved_at=retrieved_at,
        content_hash=content_hash,
        raw_html_path=str(raw_path),
        parsed_json_path=str(parsed_path),
    )


def latest_parsed_payload(cache_law_dir: Path, doc_id: str) -> dict | None:
    doc_dir = _doc_dir(cache_law_dir, doc_id)
    index = load_index(doc_dir)
    versions = index.get("versions", [])
    if not versions:
        return None
    latest = versions[-1]
    return json.loads(Path(latest["parsed_json_path"]).read_text(encoding="utf-8"))
