from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import math

from prooflens.corpus import Corpus, SourceChunk


@dataclass(frozen=True)
class RetrievedEvidence:
    chunk_id: str
    text: str
    metadata: dict[str, str]
    score: float
    citation: dict[str, str | list[str]]


class LocalMultilingualEmbedder:
    """Deterministic local embedder for multilingual text without external APIs."""

    name = "local-multilingual-hash-v1"

    def __init__(self, dimensions: int = 64) -> None:
        self._dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        normalized = " ".join(text.lower().split())
        if not normalized:
            return vector

        window = 3
        grams = [
            normalized[i : i + window]
            for i in range(max(0, len(normalized) - window + 1))
        ]
        if not grams:
            grams = [normalized]

        for gram in grams:
            digest = sha256(gram.encode("utf-8")).hexdigest()
            slot = int(digest[:8], 16) % self._dimensions
            vector[slot] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class InMemoryVectorIndex:
    """Local test-equivalent index for vector retrieval."""

    def __init__(self) -> None:
        self._entries: list[tuple[SourceChunk, list[float]]] = []

    def upsert(self, chunk: SourceChunk, embedding: list[float]) -> None:
        self._entries.append((chunk, embedding))

    def query(self, query_embedding: list[float]) -> list[tuple[SourceChunk, float]]:
        scored: list[tuple[SourceChunk, float]] = []
        for chunk, embedding in self._entries:
            score = sum(a * b for a, b in zip(query_embedding, embedding, strict=True))
            scored.append((chunk, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored


class EvidenceRetriever:
    def __init__(self, embedder: LocalMultilingualEmbedder, index: InMemoryVectorIndex) -> None:
        self._embedder = embedder
        self._index = index
        self.embedding_provider = embedder.name

    def retrieve(
        self,
        query_text: str,
        scenario_family: str,
        selected_university: str | None,
        top_k: int = 5,
    ) -> list[RetrievedEvidence]:
        query_embedding = self._embedder.embed(query_text)
        candidates = self._index.query(query_embedding)
        filtered = [
            (chunk, score)
            for chunk, score in candidates
            if chunk.metadata.get("scenario_family") == scenario_family
            and (
                selected_university is None
                or chunk.metadata.get("selected_university") == selected_university
            )
        ]

        return [
            RetrievedEvidence(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                metadata=dict(chunk.metadata),
                score=score,
                citation=_citation_from_metadata(chunk.metadata),
            )
            for chunk, score in filtered[:top_k]
        ]


def index_corpus(corpus: Corpus) -> EvidenceRetriever:
    embedder = LocalMultilingualEmbedder()
    index = InMemoryVectorIndex()
    for chunk in corpus.chunks:
        index.upsert(chunk, embedder.embed(chunk.text))
    return EvidenceRetriever(embedder=embedder, index=index)


def _citation_from_metadata(metadata: dict[str, str]) -> dict[str, str | list[str]]:
    return {
        "title": metadata["title"],
        "source_owner": metadata["source_owner"],
        "url": metadata["url"],
        "trust_level": metadata["trust_level"],
        "retrieved_at": metadata["retrieved_at"],
        "source_badges": _derive_source_badges(metadata),
    }


def _derive_source_badges(metadata: dict[str, str]) -> list[str]:
    badges = [metadata.get("trust_level", "unknown")]
    category = metadata.get("source_category")
    if category:
        badges.append(category)
    source_type = metadata.get("source_type")
    if source_type:
        badges.append(source_type)
    selected_university = metadata.get("selected_university")
    if selected_university:
        badges.append(f"selected_university:{selected_university}")
    return badges
