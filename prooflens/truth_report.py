from __future__ import annotations

from dataclasses import asdict, dataclass

from prooflens.manipulation_signals import analyze_manipulation_risk
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
    risk_analysis = analyze_manipulation_risk(normalized_text)
    evidence_state = EvidenceState(has_trusted_evidence=False, has_manipulation_signals=False)
    decision = verdict_policy.evaluate(evidence_state)

    explanation = "Bu iddia icin resmi kaynaklarda dogrudan dogrulama bulunamadi."
    if risk_analysis.signals:
        explanation += " Supheli dil kaliplari ek dikkat gerektiriyor."

    summary_message = (
        "Iddia resmi kaynaklarla su anda dogrulanamadi. Resmi kaynak kontrolu yapmadan "
        "paylasma veya odeme yapma."
    )
    if risk_analysis.signals:
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
        manipulation_signals=risk_analysis.signals,
        recommended_actions=risk_analysis.recommended_actions,
        summary={
            "tr_message": summary_message,
        },
    )


def truth_report_to_dict(report: TruthReport) -> dict[str, object]:
    return asdict(report)
