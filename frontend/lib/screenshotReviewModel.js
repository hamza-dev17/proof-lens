export function createScreenshotReviewState({
  previewUrl,
  extractedText,
  scenarioFamily,
  selectedUniversity,
  extractionSource,
  demoCaseId,
}) {
  return {
    previewUrl: previewUrl ?? null,
    extractedText,
    reviewedText: extractedText,
    scenarioFamily,
    selectedUniversity,
    extractionSource,
    demoCaseId: demoCaseId ?? null,
  };
}

export function updateReviewedText(reviewState, reviewedText) {
  return {
    ...reviewState,
    reviewedText,
  };
}

export function buildScreenshotVerificationPayload(reviewState) {
  return {
    input_type: "image",
    scenario_family: reviewState.scenarioFamily,
    selected_university: reviewState.selectedUniversity,
    reviewed_text: reviewState.reviewedText,
    ocr_text: reviewState.extractedText,
  };
}
