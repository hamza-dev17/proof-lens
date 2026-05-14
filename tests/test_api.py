import unittest

from fastapi.testclient import TestClient

from prooflens.api import app


class PastedTextVerificationApiTests(unittest.TestCase):
    def test_allows_local_nextjs_browser_origin(self):
        client = TestClient(app)

        response = client.options(
            "/verify/pasted-text",
            headers={
                "Origin": "http://127.0.0.1:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://127.0.0.1:3000")

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

    def test_optionally_saves_pasted_text_report(self):
        client = TestClient(app)
        response = client.post(
            "/verify/pasted-text",
            json={
                "input_type": "pasted_text",
                "scenario_family": "university_announcement",
                "selected_university": "GIBTU",
                "text": "GIBTU'de tum final sinavlari iptal edildi.",
                "save_report": True,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsInstance(payload.get("saved_report_id"), int)

        list_response = client.get("/reports/saved")
        self.assertEqual(list_response.status_code, 200)
        reports = list_response.json()["reports"]
        self.assertTrue(any(item["id"] == payload["saved_report_id"] for item in reports))


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

    def test_optionally_saves_screenshot_report_and_lists_history(self):
        client = TestClient(app)
        verify_response = client.post(
            "/verify/screenshot",
            json={
                "input_type": "image",
                "scenario_family": "university_announcement",
                "selected_university": "GIBTU",
                "reviewed_text": "GIBTU final sinavlari iptal edildi deniyor.",
                "ocr_text": "HIDDEN_OCR",
                "save_report": True,
            },
        )

        self.assertEqual(verify_response.status_code, 200)
        saved_report_id = verify_response.json().get("saved_report_id")
        self.assertIsInstance(saved_report_id, int)

        list_response = client.get("/reports/saved")
        self.assertEqual(list_response.status_code, 200)
        reports = list_response.json()["reports"]
        self.assertTrue(any(item["id"] == saved_report_id for item in reports))

        detail_response = client.get(f"/reports/saved/{saved_report_id}")
        self.assertEqual(detail_response.status_code, 200)
        saved_report = detail_response.json()["report"]
        self.assertNotIn("ocr_text", saved_report)
        self.assertNotIn("raw_screenshot_bytes", saved_report)


if __name__ == "__main__":
    unittest.main()
