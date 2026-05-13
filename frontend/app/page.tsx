"use client";

import { useEffect, useState } from "react";

import {
  buildScreenshotVerificationPayload,
  createScreenshotReviewState,
  updateReviewedText,
} from "../lib/screenshotReviewModel.js";

const DEMO_CASE_OPTIONS = [
  { value: "", label: "Demo secme (kendi ekran goruntumu yukleyecegim)" },
  { value: "fake-gibtu-exam-cancellation", label: "Demo: Sahte GIBTU Sinav Iptali" },
  { value: "fake-gibtu-internship-payment-announcement", label: "Demo: Sahte GIBTU Staj Odeme Duyurusu" },
  { value: "internship-scam-registration-fee", label: "Demo: Kayit Ucreti Isteyen Staj Dolandiriciligi" },
];

export default function Page() {
  const [inputMode, setInputMode] = useState("pasted_text");
  const [text, setText] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [scenarioFamily, setScenarioFamily] = useState("university_announcement");
  const [selectedDemoCaseId, setSelectedDemoCaseId] = useState("");
  const [screenshotFile, setScreenshotFile] = useState(null);
  const [screenshotPreviewUrl, setScreenshotPreviewUrl] = useState("");
  const [reviewState, setReviewState] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isVerifyingScreenshot, setIsVerifyingScreenshot] = useState(false);

  const selectedUniversity = scenarioFamily === "university_announcement" ? "GIBTU" : null;

  useEffect(() => {
    if (!screenshotFile) {
      setScreenshotPreviewUrl("");
      return undefined;
    }
    const previewUrl = URL.createObjectURL(screenshotFile);
    setScreenshotPreviewUrl(previewUrl);
    return () => URL.revokeObjectURL(previewUrl);
  }, [screenshotFile]);

  async function onSubmitPastedText(event) {
    event.preventDefault();
    setError("");

    try {
      const response = await fetch("http://localhost:8000/verify/pasted-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_type: "pasted_text",
          scenario_family: scenarioFamily,
          selected_university: selectedUniversity,
          text,
        }),
      });

      if (!response.ok) {
        throw new Error("Dogrulama istegi basarisiz oldu.");
      }

      const data = await response.json();
      setReport(data);
    } catch (submitError) {
      setError(submitError.message);
    }
  }

  async function onExtractScreenshot(event) {
    event.preventDefault();
    setError("");
    setIsExtracting(true);

    try {
      if (!selectedDemoCaseId && !screenshotFile) {
        throw new Error("Lutfen bir ekran goruntusu yukleyin veya bir demo screenshot secin.");
      }

      const formData = new FormData();
      formData.append("scenario_family", scenarioFamily);
      if (selectedUniversity !== null) {
        formData.append("selected_university", selectedUniversity);
      }
      if (selectedDemoCaseId) {
        formData.append("demo_case_id", selectedDemoCaseId);
      } else if (screenshotFile) {
        formData.append("image", screenshotFile);
      }

      const response = await fetch("http://localhost:8000/verify/screenshot/extract", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Ekran goruntusunden metin cikarma basarisiz oldu.");
      }

      const payload = await response.json();
      setReviewState(
        createScreenshotReviewState({
          previewUrl: screenshotPreviewUrl || null,
          extractedText: payload.extracted_text,
          scenarioFamily: payload.scenario_family,
          selectedUniversity: payload.selected_university,
          extractionSource: payload.extraction_source,
          demoCaseId: payload.demo_case_id ?? null,
        }),
      );
      setReport(null);
    } catch (extractError) {
      setError(extractError.message);
    } finally {
      setIsExtracting(false);
    }
  }

  async function onVerifyReviewedScreenshot(event) {
    event.preventDefault();
    if (!reviewState) {
      return;
    }
    setError("");
    setIsVerifyingScreenshot(true);

    try {
      const response = await fetch("http://localhost:8000/verify/screenshot", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildScreenshotVerificationPayload(reviewState)),
      });
      if (!response.ok) {
        throw new Error("Gozden gecirilen metinle dogrulama basarisiz oldu.");
      }
      const data = await response.json();
      setReport(data);
    } catch (verifyError) {
      setError(verifyError.message);
    } finally {
      setIsVerifyingScreenshot(false);
    }
  }

  return (
    <main style={{ maxWidth: 960, margin: "0 auto", padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <h1>ProofLens Analyzer (MVP Iskelet)</h1>
      <p>
        Senaryo: {scenarioFamily === "university_announcement" ? "Universite duyurusu" : "Staj/Is dolandiriciligi"}
        {" | "}
        Secili universite: {selectedUniversity ?? "Yok"}
      </p>

      <label htmlFor="scenario-family">Senaryo ailesi</label>
      <select
        id="scenario-family"
        value={scenarioFamily}
        onChange={(event) => {
          setScenarioFamily(event.target.value);
          setReport(null);
          setReviewState(null);
          setError("");
        }}
        style={{ display: "block", marginTop: 8, marginBottom: 12 }}
      >
        <option value="university_announcement">Universite duyurusu</option>
        <option value="internship_job_scam">Staj/is dolandiriciligi</option>
      </select>

      <div style={{ display: "flex", gap: 16, marginBottom: 16 }}>
        <label htmlFor="mode-pasted">
          <input
            id="mode-pasted"
            type="radio"
            name="input-mode"
            value="pasted_text"
            checked={inputMode === "pasted_text"}
            onChange={() => {
              setInputMode("pasted_text");
              setReviewState(null);
              setError("");
            }}
          />{" "}
          Metin yapistir
        </label>
        <label htmlFor="mode-screenshot">
          <input
            id="mode-screenshot"
            type="radio"
            name="input-mode"
            value="screenshot"
            checked={inputMode === "screenshot"}
            onChange={() => {
              setInputMode("screenshot");
              setReport(null);
              setError("");
            }}
          />{" "}
          Screenshot yukle
        </label>
      </div>

      {inputMode === "pasted_text" ? (
        <form onSubmit={onSubmitPastedText}>
          <label htmlFor="claim-text">Supheli metin</label>
          <textarea
            id="claim-text"
            value={text}
            onChange={(event) => setText(event.target.value)}
            rows={6}
            style={{ width: "100%", marginTop: 8 }}
            placeholder="Duyuru metnini buraya yapistir"
          />
          <button type="submit" style={{ marginTop: 12 }}>
            Dogrula
          </button>
        </form>
      ) : (
        <section>
          <form onSubmit={onExtractScreenshot}>
            <label htmlFor="demo-case-id">Demo screenshot (opsiyonel)</label>
            <select
              id="demo-case-id"
              value={selectedDemoCaseId}
              onChange={(event) => {
                setSelectedDemoCaseId(event.target.value);
                setReviewState(null);
                if (event.target.value) {
                  setScreenshotFile(null);
                }
              }}
              style={{ display: "block", marginTop: 8, marginBottom: 12 }}
            >
              {DEMO_CASE_OPTIONS.map((option) => (
                <option key={option.value || "none"} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <label htmlFor="screenshot-upload">Ekran goruntusu yukle</label>
            <input
              id="screenshot-upload"
              type="file"
              accept="image/*"
              disabled={Boolean(selectedDemoCaseId)}
              onChange={(event) => {
                const file = event.target.files?.[0] ?? null;
                setScreenshotFile(file);
                setReviewState(null);
              }}
              style={{ display: "block", marginTop: 8, marginBottom: 12 }}
            />

            <button type="submit" disabled={isExtracting}>
              {isExtracting ? "Metin cikariliyor..." : "Metni Cikar ve Gozden Gecir"}
            </button>
          </form>

          {reviewState ? (
            <form onSubmit={onVerifyReviewedScreenshot} style={{ marginTop: 20 }}>
              <h2>Extracted Text Review</h2>
              {reviewState.previewUrl ? (
                <img
                  src={reviewState.previewUrl}
                  alt="Yuklenen screenshot onizlemesi"
                  style={{ maxWidth: "100%", border: "1px solid #ddd", borderRadius: 8, marginBottom: 12 }}
                />
              ) : (
                <p>
                  Demo screenshot secildi: {reviewState.demoCaseId ?? "bilinmeyen demo"}
                </p>
              )}

              <label htmlFor="reviewed-text">Gozden gecirilen metin</label>
              <textarea
                id="reviewed-text"
                rows={7}
                style={{ width: "100%", marginTop: 8 }}
                value={reviewState.reviewedText}
                onChange={(event) => setReviewState(updateReviewedText(reviewState, event.target.value))}
              />
              <button type="submit" style={{ marginTop: 12 }} disabled={isVerifyingScreenshot}>
                {isVerifyingScreenshot ? "Dogrulaniyor..." : "Gozden Gecirilen Metinle Dogrula"}
              </button>
            </form>
          ) : null}
        </section>
      )}

      {error ? <p>{error}</p> : null}

      {report ? (
        <section style={{ marginTop: 24 }}>
          <h2>Truth Report</h2>
          <p>
            <strong>Genel karar:</strong> {report.overall_verdict}
          </p>
          <p>
            <strong>Guven seviyesi:</strong> {report.confidence_level}
          </p>
          <p>{report.summary?.tr_message}</p>

          <h3>Claim Cards</h3>
          <ul>
            {report.claim_cards?.map((card, index) => (
              <li key={`${card.claim_text}-${index}`}>
                {card.claim_text} - {card.verdict} ({card.confidence_level})
              </li>
            ))}
          </ul>

          <h3>Kaynaklar</h3>
          <ul>
            {report.source_citations?.map((source, index) => (
              <li key={`${source.url}-${index}`}>
                {source.title} - {source.source_owner}
              </li>
            ))}
          </ul>

          <h3>Manipulation Signals</h3>
          <ul>
            {report.manipulation_signals?.map((signal, index) => (
              <li key={`${signal}-${index}`}>{signal}</li>
            ))}
          </ul>

          <h3>Onerilen Aksiyonlar</h3>
          <ul>
            {report.recommended_actions?.map((action, index) => (
              <li key={`${action}-${index}`}>{action}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </main>
  );
}
