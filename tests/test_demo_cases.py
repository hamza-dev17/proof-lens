import unittest
from pathlib import Path

from prooflens.demo_cases import DemoCaseValidationError, load_demo_cases


class DemoCaseFixtureTests(unittest.TestCase):
    def test_loads_three_seeded_demo_cases_with_required_contract(self):
        cases = load_demo_cases(Path("fixtures/demo_cases.json"))

        self.assertEqual(len(cases), 3)
        self.assertEqual(
            [case.case_id for case in cases],
            [
                "fake-gibtu-exam-cancellation",
                "fake-gibtu-internship-payment-announcement",
                "internship-scam-registration-fee",
            ],
        )

        for case in cases:
            self.assertTrue(case.plain_text_input.strip())
            self.assertTrue(case.screenshot_fixture_path.strip())
            self.assertIn(case.scenario_family, {"university_announcement", "internship_job_scam"})

        university_cases = [case for case in cases if case.scenario_family == "university_announcement"]
        self.assertEqual(len(university_cases), 2)
        self.assertTrue(all(case.selected_university == "GIBTU" for case in university_cases))

        scam_case = next(case for case in cases if case.case_id == "internship-scam-registration-fee")
        self.assertEqual(scam_case.scenario_family, "internship_job_scam")
        self.assertIsNone(scam_case.selected_university)
        self.assertTrue(scam_case.synthetic_demo_only)
        self.assertIn("not an Official University Source", scam_case.synthetic_material_note)


if __name__ == "__main__":
    unittest.main()
