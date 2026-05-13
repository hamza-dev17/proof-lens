import test from "node:test";
import assert from "node:assert/strict";

import {
  buildScreenshotVerificationPayload,
  createScreenshotReviewState,
  updateReviewedText,
} from "../lib/screenshotReviewModel.js";

test("createScreenshotReviewState keeps extracted text editable and previewable", () => {
  const state = createScreenshotReviewState({
    previewUrl: "blob://preview",
    extractedText: "OCR text from screenshot",
    scenarioFamily: "university_announcement",
    selectedUniversity: "GIBTU",
    extractionSource: "upload",
    demoCaseId: null,
  });

  assert.equal(state.previewUrl, "blob://preview");
  assert.equal(state.extractedText, "OCR text from screenshot");
  assert.equal(state.reviewedText, "OCR text from screenshot");
});

test("buildScreenshotVerificationPayload uses reviewed text instead of hidden OCR text", () => {
  const initial = createScreenshotReviewState({
    previewUrl: null,
    extractedText: "hidden OCR",
    scenarioFamily: "university_announcement",
    selectedUniversity: "GIBTU",
    extractionSource: "demo_case",
    demoCaseId: "fake-gibtu-exam-cancellation",
  });
  const edited = updateReviewedText(initial, "user reviewed text");
  const payload = buildScreenshotVerificationPayload(edited);

  assert.equal(payload.reviewed_text, "user reviewed text");
  assert.equal(payload.ocr_text, "hidden OCR");
  assert.equal(payload.scenario_family, "university_announcement");
  assert.equal(payload.selected_university, "GIBTU");
  assert.equal(payload.save_report, false);
});

test("buildScreenshotVerificationPayload can opt in to report saving", () => {
  const state = createScreenshotReviewState({
    previewUrl: null,
    extractedText: "hidden OCR",
    scenarioFamily: "internship_job_scam",
    selectedUniversity: null,
    extractionSource: "upload",
    demoCaseId: null,
  });
  const payload = buildScreenshotVerificationPayload(state, true);
  assert.equal(payload.save_report, true);
});
