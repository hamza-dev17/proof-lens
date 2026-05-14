from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


REQUIRED_METADATA = (
    "title",
    "source_owner",
    "url",
    "trust_level",
    "retrieved_at",
    "scenario_family",
)


class SourceMetadataError(ValueError):
    """Raised when curated source metadata is incomplete or inconsistent."""


@dataclass(frozen=True)
class SourceDocument:
    path: Path
    metadata: dict[str, str]
    text: str


@dataclass(frozen=True)
class SourceChunk:
    chunk_id: str
    source_path: str
    text: str
    metadata: dict[str, str]


@dataclass(frozen=True)
class Corpus:
    sources: tuple[SourceDocument, ...]
    chunks: tuple[SourceChunk, ...]


def load_corpus(root: Path | str) -> Corpus:
    """Load curated markdown sources and prepare indexable chunks."""
    root_path = Path(root)
    sources = tuple(_load_source(path) for path in sorted(root_path.rglob("*.md")))
    chunks = tuple(
        chunk
        for source in sources
        for chunk in prepare_source_chunks(source)
    )
    return Corpus(sources=sources, chunks=chunks)


def validate_metadata(metadata: dict[str, str], source_path: Path | str = "") -> None:
    missing = [field for field in REQUIRED_METADATA if not metadata.get(field)]
    if missing:
        location = f" in {source_path}" if source_path else ""
        raise SourceMetadataError(
            f"Missing required source metadata{location}: {', '.join(missing)}"
        )

    if metadata["trust_level"] not in {"official", "trusted_guidance", "synthetic_demo"}:
        raise SourceMetadataError(
            f"Unsupported trust_level in {source_path}: {metadata['trust_level']}"
        )

    if not re.match(r"^https?://", metadata["url"]):
        raise SourceMetadataError(f"Source URL must be absolute in {source_path}")

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", metadata["retrieved_at"]):
        raise SourceMetadataError(
            f"retrieved_at must use YYYY-MM-DD format in {source_path}"
        )

    if metadata.get("selected_university") == "GIBTU":
        is_official_gibtu = (
            metadata["trust_level"] == "official"
            and metadata.get("source_category") == "official_university"
            and metadata.get("synthetic") == "false"
            and metadata["url"].startswith("https://www.gibtu.edu.tr/")
        )
        if not is_official_gibtu:
            raise SourceMetadataError(
                f"GIBTU sources must be real official university sources in {source_path}"
            )


def prepare_source_chunks(source: SourceDocument, max_chars: int = 900) -> tuple[SourceChunk, ...]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", source.text) if part.strip()]
    chunks: list[SourceChunk] = []
    current: list[str] = []
    current_size = 0

    for paragraph in paragraphs:
        if current and current_size + len(paragraph) + 2 > max_chars:
            chunks.append(_make_chunk(source, len(chunks), "\n\n".join(current)))
            current = []
            current_size = 0

        current.append(paragraph)
        current_size += len(paragraph) + 2

    if current:
        chunks.append(_make_chunk(source, len(chunks), "\n\n".join(current)))

    return tuple(chunks)


def _load_source(path: Path) -> SourceDocument:
    raw = path.read_text(encoding="utf-8")
    metadata, body = _split_front_matter(raw, path)
    validate_metadata(metadata, path)
    return SourceDocument(path=path, metadata=metadata, text=_normalize_markdown(body))


def _split_front_matter(raw: str, path: Path) -> tuple[dict[str, str], str]:
    if not raw.startswith("---\n"):
        raise SourceMetadataError(f"Missing front matter in {path}")

    try:
        _, front_matter, body = raw.split("---\n", 2)
    except ValueError as error:
        raise SourceMetadataError(f"Unclosed front matter in {path}") from error

    metadata: dict[str, str] = {}
    for line in front_matter.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise SourceMetadataError(f"Invalid metadata line in {path}: {line}")
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')

    return metadata, body


def _normalize_markdown(markdown: str) -> str:
    normalized_lines = []
    for line in markdown.replace("\r\n", "\n").splitlines():
        normalized_lines.append(re.sub(r"[ \t]+", " ", line).strip())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(normalized_lines)).strip()


def _make_chunk(source: SourceDocument, index: int, text: str) -> SourceChunk:
    source_path = source.path.as_posix()
    return SourceChunk(
        chunk_id=f"{source_path}#{index + 1}",
        source_path=source_path,
        text=text,
        metadata=dict(source.metadata),
    )
