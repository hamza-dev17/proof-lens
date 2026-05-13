from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from prooflens.corpus import load_corpus
from prooflens.retrieval import RetrievedEvidence, index_corpus
from prooflens.verdict_policy import EvidenceState, VerdictPolicy


class Retriever(Protocol):
    def retrieve(
        self,
        query_text: str,
        scenario_family: str,
        selected_university: str | None,
        top_k: int = 5,
    ) -> list[RetrievedEvidence]:
        ...


@dataclass(frozen=True)
class ClaimExtractionOutput:
    claims: tuple[str, ...]


@dataclass(frozen=True)
class RetrievalOutput:
    claim: str
    evidences: tuple[RetrievedEvidence, ...]


@dataclass(frozen=True)
class SkepticOutput:
    claim: str
    evidences: tuple[RetrievedEvidence, ...]
    retry_count: int


@dataclass(frozen=True)
class VerdictOutput:
    verdict: str
    confidence_level: str
    supporting_evidence: tuple[dict[str, str], ...]
    contradicting_evidence: tuple[dict[str, str], ...]


class VerificationWorkflow:
    def __init__(self, retriever: Retriever | None = None) -> None:
        if retriever is None:
            corpus = load_corpus(Path("trusted_sources"))
            retriever = index_corpus(corpus)
        self._retriever = retriever
        self._policy = VerdictPolicy()

    def run(
        self,
        input_text: str,
        scenario_family: str,
        selected_university: str | None,
    ) -> dict[str, object]:
        normalized_text = " ".join(input_text.split())
        extraction = self._extract_claims(normalized_text)
        claim_results = []
        for claim in extraction.claims:
            retrieval = self._retrieve(claim, scenario_family, selected_university)
            skeptical = self._skeptic(retrieval, scenario_family, selected_university)
            verdict = self._assign_verdict(claim, skeptical)
            claim_results.append((claim, skeptical, verdict))

        return self._write_report(
            text=normalized_text,
            scenario_family=scenario_family,
            selected_university=selected_university,
            claim_results=tuple(claim_results),
        )

    def _extract_claims(self, normalized_text: str) -> ClaimExtractionOutput:
        if not normalized_text:
            return ClaimExtractionOutput(claims=("Paylasilan universite duyurusu ifadesi",))

        segments = [segment.strip() for segment in normalized_text.split(".") if segment.strip()]
        conservative_claims: list[str] = []
        for segment in segments:
            lowered = segment.lower()
            if lowered.startswith("bence "):
                continue
            if len(segment.split()) < 4:
                continue
            if "hemen odeme" in lowered:
                continue
            conservative_claims.append(segment)

        if not conservative_claims:
            conservative_claims.append(normalized_text)
        return ClaimExtractionOutput(claims=tuple(conservative_claims))

    def _retrieve(
        self,
        claim: str,
        scenario_family: str,
        selected_university: str | None,
    ) -> RetrievalOutput:
        evidences = self._retriever.retrieve(
            query_text=claim,
            scenario_family=scenario_family,
            selected_university=selected_university,
            top_k=3,
        )
        return RetrievalOutput(claim=claim, evidences=tuple(evidences))

    def _skeptic(
        self,
        retrieval: RetrievalOutput,
        scenario_family: str,
        selected_university: str | None,
    ) -> SkepticOutput:
        if retrieval.evidences and retrieval.evidences[0].score >= 0.75:
            return SkepticOutput(
                claim=retrieval.claim,
                evidences=retrieval.evidences,
                retry_count=0,
            )

        rewritten_query = f"resmi duyuru: {retrieval.claim}"
        retry_evidences = self._retriever.retrieve(
            query_text=rewritten_query,
            scenario_family=scenario_family,
            selected_university=selected_university,
            top_k=3,
        )
        return SkepticOutput(
            claim=retrieval.claim,
            evidences=tuple(retry_evidences),
            retry_count=1,
        )

    def _assign_verdict(self, claim: str, skeptical: SkepticOutput) -> VerdictOutput:
        claim_l = claim.lower()
        evidence_text = " ".join(item.text.lower() for item in skeptical.evidences)
        contradict_tokens = ("iptal edildi", "iptal", "cancelled", "canceled")
        contradiction_observed = any(token in claim_l for token in contradict_tokens) and (
            "iptal edildi bilgisi yer almiyor" in evidence_text
            or "iptal edilmedi" in evidence_text
        )

        supporting = tuple(
            {"snippet": item.text, "chunk_id": item.chunk_id}
            for item in skeptical.evidences
            if not contradiction_observed
        )
        contradicting = tuple(
            {"snippet": item.text, "chunk_id": item.chunk_id}
            for item in skeptical.evidences
            if contradiction_observed
        )

        decision = self._policy.evaluate(
            EvidenceState(
                has_trusted_evidence=bool(skeptical.evidences),
                is_directly_contradicted=contradiction_observed,
                evidence_is_insufficient=skeptical.retry_count == 1 and not contradiction_observed,
                has_manipulation_signals=True,
            )
        )
        return VerdictOutput(
            verdict=decision.verdict,
            confidence_level=decision.confidence_label(),
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
        )

    def _write_report(
        self,
        text: str,
        scenario_family: str,
        selected_university: str | None,
        claim_results: tuple[tuple[str, SkepticOutput, VerdictOutput], ...],
    ) -> dict[str, object]:
        claims_payload: list[dict[str, object]] = []
        claim_cards: list[dict[str, object]] = []
        citations: list[dict[str, str]] = []
        all_claims: list[str] = []

        overall_verdict = "Dogrulanamadi"
        overall_confidence = "Dusuk guven"

        for claim, skeptical, verdict in claim_results:
            all_claims.append(claim)
            explanation = "Bu iddia icin resmi kaynaklarda dogrudan dogrulama bulunamadi."
            if skeptical.retry_count == 1:
                explanation += " Ilk arama zayif kaldigi icin bir kez yeniden arama yapildi."
            explanation += " Mesajdaki aciliyet dili ek dikkat gerektiriyor."

            sources_checked = [
                {
                    "title": evidence.citation["title"],
                    "source_owner": evidence.citation["source_owner"],
                    "trust_level": evidence.citation["trust_level"],
                    "url": evidence.citation["url"],
                    "retrieved_at": evidence.citation["retrieved_at"],
                    "snippet": evidence.text,
                }
                for evidence in skeptical.evidences
            ]
            citations.extend(
                [
                    {
                        "title": evidence.citation["title"],
                        "source_owner": evidence.citation["source_owner"],
                        "trust_level": evidence.citation["trust_level"],
                        "url": evidence.citation["url"],
                        "retrieved_at": evidence.citation["retrieved_at"],
                    }
                    for evidence in skeptical.evidences
                ]
            )

            claims_payload.append(
                {
                    "claim": claim,
                    "verdict": verdict.verdict,
                    "confidence_level": verdict.confidence_level,
                    "explanation": explanation,
                    "supporting_evidence": list(verdict.supporting_evidence),
                    "contradicting_evidence": list(verdict.contradicting_evidence),
                    "sources_checked": sources_checked,
                    "manipulation_signals": ["acil dil", "resmi kaynak yok"],
                }
            )
            claim_cards.append(
                {
                    "claim_text": claim,
                    "verdict": verdict.verdict,
                    "confidence_level": verdict.confidence_level,
                    "explanation_tr": explanation,
                    "skeptic_retry_count": skeptical.retry_count,
                    "sources_checked": sources_checked,
                }
            )

            if verdict.verdict == "Yanlis":
                overall_verdict = "Supheli"
                overall_confidence = "Orta guven"
            elif verdict.verdict == "Dogru" and overall_verdict != "Supheli":
                overall_verdict = "Dogru"
                overall_confidence = "Orta guven"

        return {
            "input_type": "pasted_text",
            "scenario_family": scenario_family,
            "selected_university": selected_university,
            "extracted_text": text,
            "checkable_claims": all_claims,
            "overall_verdict": overall_verdict,
            "confidence_level": overall_confidence,
            "overall_confidence_level": overall_confidence,
            "claims": claims_payload,
            "claim_cards": claim_cards,
            "source_citations": citations,
            "manipulation_signals": ["Acil ve kesin ifade dili"],
            "recommended_actions": [
                "Odeme yapmadan once resmi GIBTU duyurularini kontrol et.",
                "Gerekirse Ogrenci Isleri ile dogrudan iletisime gec.",
            ],
            "summary": {
                "tr_message": (
                    "Iddia resmi kaynaklarla su anda dogrulanamadi. Resmi kaynak "
                    "kontrolu yapmadan paylasma veya odeme yapma."
                )
            },
        }
