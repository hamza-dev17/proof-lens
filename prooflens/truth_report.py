from __future__ import annotations

from dataclasses import asdict, dataclass

from prooflens.verdict_policy import (
    EvidenceState,
    VerdictPolicy,
)


@dataclass(frozen=True)
class TruthReport:
    input_type: str
    scenario_family: str
    selected_university: str | None
    extracted_text: str
    checkable_claims: list[str]
    overall_verdict: str
    confidence_level: str
    claim_cards: list[dict[str, str]]
    source_citations: list[dict[str, str]]
    manipulation_signals: list[str]
    recommended_actions: list[str]
    summary: dict[str, str]


def build_stub_truth_report(text: str) -> TruthReport:
    normalized_text = " ".join(text.split())
    claim = normalized_text or "Paylasilan universite duyurusu ifadesi"

    verdict_policy = VerdictPolicy()
    evidence_state = EvidenceState(
        has_trusted_evidence=False,
        has_manipulation_signals=True,
    )
    decision = verdict_policy.evaluate(evidence_state)

    manipulation_signals = []
    if evidence_state.has_manipulation_signals:
        manipulation_signals.append("Acil ve kesin ifade dili")

    explanation = "Bu iddia icin resmi kaynaklarda dogrudan dogrulama bulunamadi."
    if evidence_state.has_manipulation_signals:
        explanation += " Mesajdaki aciliyet dili ek dikkat gerektiriyor."

    summary_message = (
        "Iddia resmi kaynaklarla su anda dogrulanamadi. Resmi kaynak kontrolu yapmadan "
        "paylasma veya odeme yapma."
    )
    if evidence_state.has_manipulation_signals:
        summary_message += " Mesajdaki yonlendirici dil guveni dusuruyor."

    return TruthReport(
        input_type="pasted_text",
        scenario_family="university_announcement",
        selected_university="GIBTU",
        extracted_text=normalized_text,
        checkable_claims=[claim],
        overall_verdict=decision.verdict,
        confidence_level=decision.confidence_label(),
        claim_cards=[
            {
                "claim_text": claim,
                "verdict": decision.verdict,
                "confidence_level": decision.confidence_label(),
                "explanation_tr": explanation,
            }
        ],
        source_citations=[
            {
                "title": "GIBTU Akademik Takvimler",
                "source_owner": "GIBTU Ogrenci Isleri Daire Baskanligi",
                "trust_level": "official",
                "url": "https://www.gibtu.edu.tr/ogrenciisleri/icerik/31231/akademik-takvimler",
                "retrieved_at": "2026-05-12",
            }
        ],
        manipulation_signals=manipulation_signals,
        recommended_actions=[
            "Odeme yapmadan once resmi GIBTU duyurularini kontrol et.",
            "Gerekirse Ogrenci Isleri ile dogrudan iletisime gec.",
        ],
        summary={
            "tr_message": summary_message,
        },
    )


def truth_report_to_dict(report: TruthReport) -> dict[str, object]:
    return asdict(report)
