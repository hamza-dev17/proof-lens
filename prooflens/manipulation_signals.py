from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManipulationAnalysis:
    signals: list[str]
    recommended_actions: list[str]


def analyze_manipulation_risk(text: str) -> ManipulationAnalysis:
    lowered = text.lower()
    signals: list[str] = []

    if any(token in lowered for token in ("hemen", "son dakika", "acele", "simdi")):
        signals.append("Acil ve baski kuran ifade dili")
    if any(token in lowered for token in ("odeme", "iban", "ucret", "kapora")):
        signals.append("Odeme veya para transferi talebi")
    if any(token in lowered for token in ("yetkili", "resmi kisi", "yonetim adina")):
        signals.append("Kimligi belirsiz otoriteye atif")
    if not any(token in lowered for token in ("202", "tarih", "bugun", "yarin")):
        signals.append("Tarih bilgisi eksik")
    if not any(token in lowered for token in ("gibtu.edu.tr", "resmi", "duyuru", "kaynak")):
        signals.append("Resmi kaynak baglantisi veya atfi yok")

    actions = [
        "Icerigi resmi kurum duyurulari ile karsilastir ve kaynagi dogrula.",
        "Supheli mesaji arkadaslarina yaymadan once ekran goruntusu ve linki birlikte kontrol et.",
    ]
    if any("Odeme" in signal for signal in signals):
        actions.insert(0, "Odeme yapmadan once mutlaka resmi kaynaklardan dogrulama yap.")

    return ManipulationAnalysis(signals=signals, recommended_actions=actions)
