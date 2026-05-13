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

    def test_accepts_internship_job_scam_without_selected_university(self):
        client = TestClient(app)

        response = client.post(
            "/verify/pasted-text",
            json={
                "input_type": "pasted_text",
                "scenario_family": "internship_job_scam",
                "selected_university": None,
                "text": "Limited slots, pay 750 TL registration fee now to start job today.",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["scenario_family"], "internship_job_scam")
        self.assertIsNone(payload["selected_university"])
        self.assertIn("resmi kaynak", payload["summary"]["tr_message"].lower())

    def test_rejects_unknown_scenario_family(self):
        client = TestClient(app)

        response = client.post(
            "/verify/pasted-text",
            json={
                "input_type": "pasted_text",
                "scenario_family": "sports_rumor",
                "selected_university": None,
                "text": "Some random claim",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("scenario_family must be one of", response.json()["detail"])


class ScreenshotVerificationApiTests(unittest.TestCase):
    def test_extracts_text_from_demo_case_screenshot_contract(self):
        client = TestClient(app)

        response = client.post(
            "/verify/screenshot/extract",
            data={
                "scenario_family": "university_announcement",
                "selected_university": "GIBTU",
                "demo_case_id": "fake-gibtu-exam-cancellation",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["input_type"], "image")
        self.assertEqual(payload["scenario_family"], "university_announcement")
        self.assertEqual(payload["selected_university"], "GIBTU")
        self.assertEqual(payload["extraction_source"], "demo_case")
        self.assertEqual(payload["demo_case_id"], "fake-gibtu-exam-cancellation")
        self.assertIn("16 Mayis 2026", payload["extracted_text"])

    def test_extracts_text_from_uploaded_screenshot(self):
        client = TestClient(app)

        response = client.post(
            "/verify/screenshot/extract",
            data={
                "scenario_family": "university_announcement",
                "selected_university": "GIBTU",
            },
            files={
                "image": ("claim.png", b"fake image bytes", "image/png"),
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["input_type"], "image")
        self.assertEqual(payload["extraction_source"], "upload")
        self.assertIn("OCR", payload["extracted_text"])

    def test_extract_requires_upload_or_demo_case(self):
        client = TestClient(app)

        response = client.post(
            "/verify/screenshot/extract",
            data={
                "scenario_family": "university_announcement",
                "selected_university": "GIBTU",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Provide either image upload or demo_case_id", response.json()["detail"])

    def test_verify_uses_reviewed_text_not_hidden_ocr_text(self):
        client = TestClient(app)

        response = client.post(
            "/verify/screenshot",
            json={
                "input_type": "image",
                "scenario_family": "university_announcement",
                "selected_university": "GIBTU",
                "reviewed_text": "GIBTU final sinavlari iptal edildi deniyor.",
                "ocr_text": "IGNORE_THIS_HIDDEN_OCR_OUTPUT",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["input_type"], "image")
        self.assertEqual(payload["extracted_text"], "GIBTU final sinavlari iptal edildi deniyor.")
        flattened_claims = " ".join(payload["checkable_claims"])
        self.assertNotIn("IGNORE_THIS_HIDDEN_OCR_OUTPUT", flattened_claims)


if __name__ == "__main__":
    unittest.main()
