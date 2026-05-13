import unittest
from unittest.mock import patch

from prooflens.retrieval import RetrievedEvidence
from prooflens.verification_workflow import VerificationWorkflow


class _FakeRetriever:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def retrieve(
        self,
        query_text: str,
        scenario_family: str,
        selected_university: str | None,
        top_k: int = 5,
    ) -> list[RetrievedEvidence]:
        self.calls.append(query_text)
        if len(self.calls) == 1:
            return []
        return [
            RetrievedEvidence(
                chunk_id="trusted_sources/universities/gibtu/announcements.md#1",
                text="Resmi duyurular Ogrenci Isleri sayfasinda yayinlanir.",
                metadata={
                    "title": "GIBTU Duyurular",
                    "source_owner": "GIBTU Ogrenci Isleri",
                    "url": "https://www.gibtu.edu.tr/ogrenciisleri",
                    "trust_level": "official",
                    "retrieved_at": "2026-05-12",
                },
                score=0.62,
                citation={
                    "title": "GIBTU Duyurular",
                    "source_owner": "GIBTU Ogrenci Isleri",
                    "url": "https://www.gibtu.edu.tr/ogrenciisleri",
                    "trust_level": "official",
                    "retrieved_at": "2026-05-12",
                    "source_badges": ["official"],
                },
            )
        ]


class _StrongEvidenceRetriever:
    def retrieve(
        self,
        query_text: str,
        scenario_family: str,
        selected_university: str | None,
        top_k: int = 5,
    ) -> list[RetrievedEvidence]:
        return [
            RetrievedEvidence(
                chunk_id="trusted_sources/universities/gibtu/academic-calendar.md#1",
                text="Akademik takvimde final sinavlari iptal edildi bilgisi yer almiyor.",
                metadata={
                    "title": "GIBTU Akademik Takvim",
                    "source_owner": "GIBTU Ogrenci Isleri",
                    "url": "https://www.gibtu.edu.tr/ogrenciisleri/icerik/31231/akademik-takvimler",
                    "trust_level": "official",
                    "retrieved_at": "2026-05-12",
                },
                score=0.92,
                citation={
                    "title": "GIBTU Akademik Takvim",
                    "source_owner": "GIBTU Ogrenci Isleri",
                    "url": "https://www.gibtu.edu.tr/ogrenciisleri/icerik/31231/akademik-takvimler",
                    "trust_level": "official",
                    "retrieved_at": "2026-05-12",
                    "source_badges": ["official"],
                },
            )
        ]


class VerificationWorkflowTests(unittest.TestCase):
    def test_skeptic_retries_once_and_report_stays_turkish(self):
        retriever = _FakeRetriever()
        workflow = VerificationWorkflow(retriever=retriever)

        with patch("urllib.request.urlopen") as mocked_urlopen:
            report = workflow.run(
                input_text="All finals at GIBTU are cancelled immediately.",
                scenario_family="university_announcement",
                selected_university="GIBTU",
            )

        self.assertEqual(len(retriever.calls), 2)
        self.assertEqual(report["input_type"], "pasted_text")
        self.assertEqual(report["overall_verdict"], "Dogrulanamadi")
        self.assertEqual(report["claim_cards"][0]["skeptic_retry_count"], 1)
        self.assertIn("resmi kaynak", report["claim_cards"][0]["explanation_tr"].lower())
        self.assertIn("resmi kaynak", report["summary"]["tr_message"].lower())
        mocked_urlopen.assert_not_called()

    def test_claim_extractor_returns_conservative_checkable_claims(self):
        workflow = VerificationWorkflow(retriever=_StrongEvidenceRetriever())

        report = workflow.run(
            input_text=(
                "GIBTU'de tum final sinavlari iptal edildi! "
                "Herkes hemen odeme yapsin. "
                "Bence bu sistem cok kotu."
            ),
            scenario_family="university_announcement",
            selected_university="GIBTU",
        )

        self.assertGreaterEqual(len(report["checkable_claims"]), 1)
        self.assertEqual(len(report["claims"]), len(report["checkable_claims"]))
        self.assertTrue(all(claim.strip() for claim in report["checkable_claims"]))

    def test_workflow_returns_truth_report_contract_with_claims_array(self):
        workflow = VerificationWorkflow(retriever=_StrongEvidenceRetriever())

        report = workflow.run(
            input_text="GIBTU final sinavlari iptal edildi deniyor.",
            scenario_family="university_announcement",
            selected_university="GIBTU",
        )

        self.assertIn("claims", report)
        self.assertTrue(report["claims"])
        first_claim = report["claims"][0]
        self.assertIn(first_claim["verdict"], {"Dogru", "Yanlis", "Yaniltici", "Dogrulanamadi"})
        self.assertIn(first_claim["confidence_level"], {"Yuksek guven", "Orta guven", "Dusuk guven"})
        self.assertIn("supporting_evidence", first_claim)
        self.assertIn("contradicting_evidence", first_claim)
        self.assertIn("sources_checked", first_claim)
        self.assertIn("manipulation_signals", first_claim)

    def test_skeptic_does_not_retry_when_evidence_is_strong(self):
        workflow = VerificationWorkflow(retriever=_StrongEvidenceRetriever())
        report = workflow.run(
            input_text="GIBTU final sinavlari iptal edildi deniyor.",
            scenario_family="university_announcement",
            selected_university="GIBTU",
        )
        self.assertEqual(report["claim_cards"][0]["skeptic_retry_count"], 0)


if __name__ == "__main__":
    unittest.main()
