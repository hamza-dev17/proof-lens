from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from prooflens.image_extraction import (
    ScreenshotExtractionUnsupported,
    build_default_screenshot_service,
)
from prooflens.verification_workflow import VerificationWorkflow


class PastedTextRequest(BaseModel):
    input_type: str
    scenario_family: str
    selected_university: str | None = None
    text: str


class ScreenshotVerificationRequest(BaseModel):
    input_type: str
    scenario_family: str
    selected_university: str | None = None
    reviewed_text: str
    ocr_text: str | None = None


app = FastAPI(title="ProofLens API", version="0.1.0")
workflow = VerificationWorkflow()
screenshot_service = build_default_screenshot_service()


def _validate_scenario(scenario_family: str, selected_university: str | None) -> None:
    allowed_scenarios = {"university_announcement", "internship_job_scam"}
    if scenario_family not in allowed_scenarios:
        raise HTTPException(
            status_code=400,
            detail="scenario_family must be one of university_announcement or internship_job_scam",
        )
    if scenario_family == "university_announcement":
        if selected_university != "GIBTU":
            raise HTTPException(status_code=400, detail="selected_university must be GIBTU")
    elif selected_university is not None:
        raise HTTPException(
            status_code=400,
            detail="selected_university must be null for internship_job_scam",
        )


@app.post("/verify/pasted-text")
def verify_pasted_text(payload: PastedTextRequest) -> dict[str, object]:
    if payload.input_type != "pasted_text":
        raise HTTPException(status_code=400, detail="input_type must be pasted_text")
    _validate_scenario(payload.scenario_family, payload.selected_university)

    return workflow.run(
        input_text=payload.text,
        scenario_family=payload.scenario_family,
        selected_university=payload.selected_university,
    )


@app.post("/verify/screenshot/extract")
async def extract_screenshot_text(
    scenario_family: str = Form(...),
    selected_university: str | None = Form(None),
    demo_case_id: str | None = Form(None),
    image: UploadFile | None = File(None),
) -> dict[str, object]:
    _validate_scenario(scenario_family, selected_university)

    if bool(demo_case_id) == bool(image):
        raise HTTPException(
            status_code=400,
            detail="Provide either image upload or demo_case_id",
        )

    if demo_case_id:
        try:
            review_payload = screenshot_service.extract_from_demo_case(demo_case_id)
        except ScreenshotExtractionUnsupported as error:
            raise HTTPException(status_code=400, detail=str(error)) from error

        if (
            review_payload.scenario_family != scenario_family
            or review_payload.selected_university != selected_university
        ):
            raise HTTPException(
                status_code=400,
                detail="demo_case_id does not match selected scenario/university",
            )
        return asdict(review_payload)

    assert image is not None
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")

    review_payload = screenshot_service.extract_from_upload(
        image_bytes=image_bytes,
        filename=image.filename or "upload.png",
        scenario_family=scenario_family,
        selected_university=selected_university,
    )
    return asdict(review_payload)


@app.post("/verify/screenshot")
def verify_reviewed_screenshot_text(payload: ScreenshotVerificationRequest) -> dict[str, object]:
    if payload.input_type != "image":
        raise HTTPException(status_code=400, detail="input_type must be image")
    _validate_scenario(payload.scenario_family, payload.selected_university)

    reviewed_text = " ".join(payload.reviewed_text.split())
    if not reviewed_text:
        raise HTTPException(status_code=400, detail="reviewed_text must not be empty")

    report = workflow.run(
        input_text=reviewed_text,
        scenario_family=payload.scenario_family,
        selected_university=payload.selected_university,
    )
    report["input_type"] = "image"
    report["extracted_text"] = reviewed_text
    return report
