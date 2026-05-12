from __future__ import annotations

from dataclasses import asdict, dataclass


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

    return TruthReport(
        input_type="pasted_text",
        scenario_family="university_announcement",
        selected_university="GIBTU",
        extracted_text=normalized_text,
        checkable_claims=[claim],
        overall_verdict="Dogrulanamadi",
        confidence_level="Dusuk guven",
        claim_cards=[
            {
                "claim_text": claim,
                "verdict": "Dogrulanamadi",
                "confidence_level": "Dusuk guven",
                "explanation_tr": "Bu iddia icin resmi kaynaklarda dogrudan dogrulama bulunamadi.",
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
        manipulation_signals=["Acil ve kesin ifade dili"],
        recommended_actions=[
            "Odeme yapmadan once resmi GIBTU duyurularini kontrol et.",
            "Gerekirse Ogrenci Isleri ile dogrudan iletisime gec.",
        ],
        summary={
            "tr_message": "Iddia resmi kaynaklarla su anda dogrulanamadi. Resmi kaynak kontrolu yapmadan paylasma veya odeme yapma.",
        },
    )


def truth_report_to_dict(report: TruthReport) -> dict[str, object]:
    return asdict(report)
