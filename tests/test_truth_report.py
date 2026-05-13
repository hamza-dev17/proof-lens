import unittest

from prooflens.truth_report import build_stub_truth_report, truth_report_to_dict


class TruthReportTests(unittest.TestCase):
    def test_build_stub_truth_report_uses_policy_outputs_consistently(self):
        report = build_stub_truth_report("GIBTU'de tum final sinavlari iptal edildi.")

        self.assertEqual(report.overall_verdict, "Dogrulanamadi")
        self.assertEqual(report.confidence_level, "Dusuk guven")
        self.assertEqual(report.claim_cards[0]["verdict"], report.overall_verdict)
        self.assertEqual(report.claim_cards[0]["confidence_level"], report.confidence_level)

    def test_build_stub_truth_report_surfaces_manipulation_signals_in_text_fields(self):
        report = build_stub_truth_report("Bunu hemen paylasin yoksa gec kalirsiniz.")

        self.assertIn("Acil ve kesin ifade dili", report.manipulation_signals)
        self.assertIn("ek dikkat", report.claim_cards[0]["explanation_tr"].lower())
        self.assertIn("yonlendirici dil", report.summary["tr_message"].lower())

    def test_truth_report_to_dict_preserves_expected_payload_shape(self):
        payload = truth_report_to_dict(build_stub_truth_report("Deneme metni"))

        self.assertEqual(payload["overall_verdict"], "Dogrulanamadi")
        self.assertEqual(payload["confidence_level"], "Dusuk guven")
        self.assertTrue(payload["source_citations"])
        self.assertEqual(payload["claim_cards"][0]["confidence_level"], payload["confidence_level"])


if __name__ == "__main__":
    unittest.main()
