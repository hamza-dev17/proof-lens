from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


ALLOWED_SCENARIO_FAMILIES = {"university_announcement", "internship_job_scam"}


class DemoCaseValidationError(ValueError):
    """Raised when demo-case fixtures are missing required fields or are inconsistent."""


@dataclass(frozen=True)
class DemoCase:
    case_id: str
    title: str
    scenario_family: str
    plain_text_input: str
    screenshot_fixture_path: str
    screenshot_contract: str
    selected_university: str | None
    synthetic_demo_only: bool
    synthetic_material_note: str


def load_demo_cases(path: Path | str) -> tuple[DemoCase, ...]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8-sig"))

    if not isinstance(payload, list):
        raise DemoCaseValidationError("Demo fixtures must be a list")

    cases = tuple(_validate_case(item, fixture_path) for item in payload)
    cases_by_id = {case.case_id: case for case in cases}

    required_case_ids = {
        "fake-gibtu-exam-cancellation",
        "fake-gibtu-internship-payment-announcement",
        "internship-scam-registration-fee",
    }

    missing_case_ids = required_case_ids - set(cases_by_id)
    if missing_case_ids:
        raise DemoCaseValidationError(
            f"Missing required demo cases: {', '.join(sorted(missing_case_ids))}"
        )

    university_cases = [
        case for case in cases if case.scenario_family == "university_announcement"
    ]
    if any(case.selected_university != "GIBTU" for case in university_cases):
        raise DemoCaseValidationError(
            "University demo cases must set selected_university to GIBTU"
        )

    internship_case = cases_by_id["internship-scam-registration-fee"]
    if internship_case.selected_university is not None:
        raise DemoCaseValidationError(
            "Internship scam case must not set selected_university"
        )
    if not internship_case.synthetic_demo_only:
        raise DemoCaseValidationError(
            "Internship scam case must be marked synthetic_demo_only"
        )

    return tuple(sorted(cases, key=lambda case: case.case_id))


def _validate_case(item: object, fixture_path: Path) -> DemoCase:
    if not isinstance(item, dict):
        raise DemoCaseValidationError(
            f"Each demo fixture in {fixture_path} must be an object"
        )

    required_fields = (
        "case_id",
        "title",
        "scenario_family",
        "plain_text_input",
        "screenshot_fixture_path",
        "screenshot_contract",
        "synthetic_demo_only",
        "synthetic_material_note",
    )
    missing_fields = [field for field in required_fields if not item.get(field)]
    if missing_fields:
        raise DemoCaseValidationError(
            f"Missing required demo fixture fields in {fixture_path}: {', '.join(missing_fields)}"
        )

    scenario_family = str(item["scenario_family"])
    if scenario_family not in ALLOWED_SCENARIO_FAMILIES:
        raise DemoCaseValidationError(
            f"Unsupported scenario_family in {fixture_path}: {scenario_family}"
        )

    synthetic_material_note = str(item["synthetic_material_note"])
    if "Official University Source" not in synthetic_material_note:
        raise DemoCaseValidationError(
            "synthetic_material_note must clarify separation from Official University Sources"
        )

    selected_university = item.get("selected_university")
    if selected_university == "":
        selected_university = None

    return DemoCase(
        case_id=str(item["case_id"]),
        title=str(item["title"]),
        scenario_family=scenario_family,
        plain_text_input=str(item["plain_text_input"]),
        screenshot_fixture_path=str(item["screenshot_fixture_path"]),
        screenshot_contract=str(item["screenshot_contract"]),
        selected_university=selected_university,
        synthetic_demo_only=bool(item["synthetic_demo_only"]),
        synthetic_material_note=synthetic_material_note,
    )
