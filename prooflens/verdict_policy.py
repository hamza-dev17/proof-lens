from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConfidenceBand(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class EvidenceState:
    has_trusted_evidence: bool
    is_directly_contradicted: bool = False
    evidence_is_insufficient: bool = False
    has_partial_truth: bool = False
    has_missing_context: bool = False
    has_exaggeration: bool = False
    has_unsupported_implication: bool = False
    has_manipulation_signals: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    verdict: str
    confidence: ConfidenceBand

    def confidence_label(self) -> str:
        return confidence_label(self.confidence)


class VerdictPolicy:
    """Authoritative mapping from evidence state to ProofLens verdict semantics."""

    def decide(self, state: EvidenceState) -> str:
        if state.is_directly_contradicted:
            return "Yanlis"

        if not state.has_trusted_evidence or state.evidence_is_insufficient:
            return "Dogrulanamadi"

        if any(
            (
                state.has_partial_truth,
                state.has_missing_context,
                state.has_exaggeration,
                state.has_unsupported_implication,
            )
        ):
            return "Yaniltici"

        return "Dogru"

    def confidence_for(self, state: EvidenceState) -> ConfidenceBand:
        if not state.has_trusted_evidence or state.evidence_is_insufficient:
            return ConfidenceBand.LOW

        if state.has_manipulation_signals:
            return ConfidenceBand.MEDIUM

        if any(
            (
                state.has_partial_truth,
                state.has_missing_context,
                state.has_exaggeration,
                state.has_unsupported_implication,
            )
        ):
            return ConfidenceBand.MEDIUM

        return ConfidenceBand.HIGH

    def evaluate(self, state: EvidenceState) -> PolicyDecision:
        return PolicyDecision(
            verdict=self.decide(state),
            confidence=self.confidence_for(state),
        )


def confidence_label(band: ConfidenceBand) -> str:
    if band is ConfidenceBand.HIGH:
        return "Yuksek guven"
    if band is ConfidenceBand.MEDIUM:
        return "Orta guven"
    return "Dusuk guven"
