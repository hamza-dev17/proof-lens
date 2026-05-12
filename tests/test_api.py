import unittest

from fastapi.testclient import TestClient

from prooflens.api import app


class PastedTextVerificationApiTests(unittest.TestCase):
    def test_returns_structured_turkish_truth_report_for_gibtu_university_claim(self):
        client = TestClient(app)

        response = client.post(
            "/verify/pasted-text",
            json={
                "input_type": "pasted_text",
                "scenario_family": "university_announcement",
                "selected_university": "GIBTU",
                "text": "GIBTU'de tum final sinavlari iptal edildi.",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["input_type"], "pasted_text")
        self.assertEqual(payload["scenario_family"], "university_announcement")
        self.assertEqual(payload["selected_university"], "GIBTU")
        self.assertEqual(payload["overall_verdict"], "Dogrulanamadi")
        self.assertIn(payload["confidence_level"], {"Dusuk guven", "Orta guven", "Yuksek guven"})

        self.assertTrue(payload["checkable_claims"])
        self.assertTrue(payload["claim_cards"])
        self.assertTrue(payload["source_citations"])
        self.assertIn("manipulation_signals", payload)
        self.assertIn("recommended_actions", payload)
        self.assertIn("resmi kaynak", payload["summary"]["tr_message"].lower())


if __name__ == "__main__":
    unittest.main()
