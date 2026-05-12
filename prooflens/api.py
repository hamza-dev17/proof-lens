from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from prooflens.truth_report import build_stub_truth_report, truth_report_to_dict


class PastedTextRequest(BaseModel):
    input_type: str
    scenario_family: str
    selected_university: str
    text: str


app = FastAPI(title="ProofLens API", version="0.1.0")


@app.post("/verify/pasted-text")
def verify_pasted_text(payload: PastedTextRequest) -> dict[str, object]:
    if payload.input_type != "pasted_text":
        raise HTTPException(status_code=400, detail="input_type must be pasted_text")
    if payload.scenario_family != "university_announcement":
        raise HTTPException(
            status_code=400,
            detail="scenario_family must be university_announcement for this slice",
        )
    if payload.selected_university != "GIBTU":
        raise HTTPException(status_code=400, detail="selected_university must be GIBTU")

    report = build_stub_truth_report(payload.text)
    return truth_report_to_dict(report)
