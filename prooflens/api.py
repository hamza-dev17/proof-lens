from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from prooflens.verification_workflow import VerificationWorkflow


class PastedTextRequest(BaseModel):
    input_type: str
    scenario_family: str
    selected_university: str | None = None
    text: str


app = FastAPI(title="ProofLens API", version="0.1.0")
workflow = VerificationWorkflow()


@app.post("/verify/pasted-text")
def verify_pasted_text(payload: PastedTextRequest) -> dict[str, object]:
    if payload.input_type != "pasted_text":
        raise HTTPException(status_code=400, detail="input_type must be pasted_text")
    allowed_scenarios = {"university_announcement", "internship_job_scam"}
    if payload.scenario_family not in allowed_scenarios:
        raise HTTPException(
            status_code=400,
            detail="scenario_family must be one of university_announcement or internship_job_scam",
        )
    if payload.scenario_family == "university_announcement":
        if payload.selected_university != "GIBTU":
            raise HTTPException(status_code=400, detail="selected_university must be GIBTU")
    elif payload.selected_university is not None:
        raise HTTPException(
            status_code=400,
            detail="selected_university must be null for internship_job_scam",
        )

    return workflow.run(
        input_text=payload.text,
        scenario_family=payload.scenario_family,
        selected_university=payload.selected_university,
    )
