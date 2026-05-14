import unittest

from prooflens.verdict_policy import (
    ConfidenceBand,
    EvidenceState,
    PolicyDecision,
    VerdictPolicy,
    confidence_label,
)


class VerdictPolicyTests(unittest.TestCase):
    def test_direct_contradiction_maps_to_yanlis(self):
        verdict = VerdictPolicy().decide(
            EvidenceState(
                has_trusted_evidence=True,
                is_directly_contradicted=True,
            )
        )
        self.assertEqual(verdict, "Yanlis")

    def test_missing_or_insufficient_evidence_maps_to_dogrulanamadi(self):
        policy = VerdictPolicy()
        self.assertEqual(
            policy.decide(EvidenceState(has_trusted_evidence=False)),
            "Dogrulanamadi",
        )
        self.assertEqual(
            policy.decide(
                EvidenceState(
                    has_trusted_evidence=True,
                    evidence_is_insufficient=True,
                )
            ),
            "Dogrulanamadi",
        )

    def test_partial_truth_or_missing_context_or_exaggeration_maps_to_yaniltici(self):
        policy = VerdictPolicy()
        self.assertEqual(
            policy.decide(EvidenceState(has_trusted_evidence=True, has_partial_truth=True)),
            "Yaniltici",
        )
        self.assertEqual(
            policy.decide(EvidenceState(has_trusted_evidence=True, has_missing_context=True)),
            "Yaniltici",
        )
        self.assertEqual(
            policy.decide(EvidenceState(has_trusted_evidence=True, has_exaggeration=True)),
            "Yaniltici",
        )
        self.assertEqual(
            policy.decide(EvidenceState(has_trusted_evidence=True, has_unsupported_implication=True)),
            "Yaniltici",
        )

    def test_manipulation_signals_alone_do_not_force_yanlis(self):
        decision = VerdictPolicy().evaluate(
            EvidenceState(
                has_trusted_evidence=False,
                has_manipulation_signals=True,
            )
        )
        self.assertEqual(decision.verdict, "Dogrulanamadi")
        self.assertEqual(decision.confidence, ConfidenceBand.LOW)

    def test_manipulation_signals_reduce_confidence_when_trusted_evidence_exists(self):
        decision = VerdictPolicy().evaluate(
            EvidenceState(
                has_trusted_evidence=True,
                has_manipulation_signals=True,
            )
        )
        self.assertEqual(decision.verdict, "Dogru")
        self.assertEqual(decision.confidence, ConfidenceBand.MEDIUM)

    def test_confidence_labels_are_turkish_bands_without_percentages(self):
        labels = {
            confidence_label(ConfidenceBand.HIGH),
            confidence_label(ConfidenceBand.MEDIUM),
            confidence_label(ConfidenceBand.LOW),
        }
        self.assertEqual(labels, {"Yuksek guven", "Orta guven", "Dusuk guven"})
        self.assertTrue(all("%" not in label for label in labels))

    def test_policy_decision_exposes_localized_confidence_label(self):
        decision = PolicyDecision(verdict="Dogru", confidence=ConfidenceBand.HIGH)
        self.assertEqual(decision.confidence_label(), "Yuksek guven")


if __name__ == "__main__":
    unittest.main()
