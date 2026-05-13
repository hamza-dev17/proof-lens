"use client";

import { useEffect, useMemo, useState } from "react";

import {
  buildAnalyzerControlState,
  buildAnalyzerViewModel,
  VERIFICATION_TIMELINE_STEPS,
} from "../lib/analyzerViewModel.js";
import { getApiBaseUrl } from "../lib/apiConfig.js";
import {
  buildScreenshotVerificationPayload,
  createScreenshotReviewState,
  updateReviewedText,
} from "../lib/screenshotReviewModel.js";

const DEMO_CASES = [
  {
    value: "fake-gibtu-exam-cancellation",
    title: "Sahte GİBTÜ sınav iptali",
    scenarioFamily: "university_announcement",
    selectedUniversity: "GIBTU",
    text: "GİBTÜ adına paylaşılan mesaj: 16 Mayıs 2026 tarihli tüm final sınavları iptal edildi.",
  },
  {
    value: "fake-gibtu-internship-payment-announcement",
    title: "Sahte GİBTÜ staj ödeme duyurusu",
    scenarioFamily: "university_announcement",
    selectedUniversity: "GIBTU",
    text: "Zorunlu staj listesine girmek için 500 TL kayıt ödemesi istendiği iddia ediliyor.",
  },
  {
    value: "internship-scam-registration-fee",
    title: "Kayıt ücreti isteyen staj ilanı",
    scenarioFamily: "internship_job_scam",
    selectedUniversity: null,
    text: "Kontenjan sınırlı, aynı gün işe alım için 750 TL kayıt ücreti yatırman gerekiyor.",
  },
];

export default function Page() {
  const [inputMode, setInputMode] = useState("pasted_text");
  const [text, setText] = useState(DEMO_CASES[0].text);
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [scenarioFamily, setScenarioFamily] = useState("university_announcement");
  const [selectedUniversity, setSelectedUniversity] = useState("GIBTU");
  const [selectedDemoCaseId, setSelectedDemoCaseId] = useState(DEMO_CASES[0].value);
  const [screenshotFile, setScreenshotFile] = useState(null);
  const [screenshotPreviewUrl, setScreenshotPreviewUrl] = useState("");
  const [reviewState, setReviewState] = useState(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [saveReport, setSaveReport] = useState(false);
  const [savedReports, setSavedReports] = useState([]);
  const [savedReportsError, setSavedReportsError] = useState("");
  const [isLoadingSavedReports, setIsLoadingSavedReports] = useState(false);

  const controls = buildAnalyzerControlState(scenarioFamily, selectedUniversity);
  const apiBaseUrl = getApiBaseUrl();
  const effectiveUniversity = controls.selectedUniversity;
  const reportModel = report ? buildAnalyzerViewModel(report) : null;
  const availableDemoCases = DEMO_CASES.filter((demoCase) => {
    if (demoCase.scenarioFamily !== scenarioFamily) {
      return false;
    }
    return demoCase.selectedUniversity === null || demoCase.selectedUniversity === effectiveUniversity;
  });
  const selectedDemoCase = DEMO_CASES.find((demoCase) => demoCase.value === selectedDemoCaseId) ?? null;
  const timeline = useMemo(
    () => buildTimelineState(Boolean(reportModel), Boolean(reviewState), isExtracting || isVerifying),
    [reportModel, reviewState, isExtracting, isVerifying],
  );

  useEffect(() => {
    if (!screenshotFile) {
      setScreenshotPreviewUrl("");
      return undefined;
    }

    const previewUrl = URL.createObjectURL(screenshotFile);
    setScreenshotPreviewUrl(previewUrl);
    return () => URL.revokeObjectURL(previewUrl);
  }, [screenshotFile]);

  function resetAnalysisState() {
    setReport(null);
    setReviewState(null);
    setError("");
  }

  function onScenarioChange(nextScenarioFamily) {
    const nextUniversity = nextScenarioFamily === "university_announcement" ? "GIBTU" : null;
    const firstDemo = DEMO_CASES.find(
      (demoCase) =>
        demoCase.scenarioFamily === nextScenarioFamily &&
        (demoCase.selectedUniversity === null || demoCase.selectedUniversity === nextUniversity),
    );

    setScenarioFamily(nextScenarioFamily);
    setSelectedUniversity(nextUniversity);
    setSelectedDemoCaseId(firstDemo?.value ?? "");
    setText(firstDemo?.text ?? "");
    resetAnalysisState();
  }

  function onUniversityChange(nextUniversity) {
    const firstDemo = DEMO_CASES.find(
      (demoCase) => demoCase.scenarioFamily === scenarioFamily && demoCase.selectedUniversity === nextUniversity,
    );

    setSelectedUniversity(nextUniversity);
    setSelectedDemoCaseId(firstDemo?.value ?? "");
    setText(firstDemo?.text ?? "");
    resetAnalysisState();
  }

  function onDemoCaseChange(nextDemoCaseId) {
    const demoCase = DEMO_CASES.find((item) => item.value === nextDemoCaseId);
    setSelectedDemoCaseId(nextDemoCaseId);
    setScreenshotFile(null);
    setReviewState(null);
    setReport(null);
    setError("");
    if (demoCase) {
      setText(demoCase.text);
    }
  }

  async function onSubmitPastedText(event) {
    event.preventDefault();
    setError("");
    setIsVerifying(true);

    try {
      const response = await fetch(`${apiBaseUrl}/verify/pasted-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input_type: "pasted_text",
          scenario_family: scenarioFamily,
          selected_university: effectiveUniversity,
          text,
          save_report: saveReport,
        }),
      });

      if (!response.ok) {
        throw new Error("Doğrulama isteği başarısız oldu.");
      }

      const data = await response.json();
      setReport(data);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setIsVerifying(false);
    }
  }

  async function onExtractScreenshot(event) {
    event.preventDefault();
    setError("");
    setIsExtracting(true);

    try {
      if (!selectedDemoCaseId && !screenshotFile) {
        throw new Error("Lütfen bir ekran görüntüsü yükleyin veya bir demo screenshot seçin.");
      }

      const formData = new FormData();
      formData.append("scenario_family", scenarioFamily);
      if (effectiveUniversity !== null) {
        formData.append("selected_university", effectiveUniversity);
      }
      if (selectedDemoCaseId) {
        formData.append("demo_case_id", selectedDemoCaseId);
      } else if (screenshotFile) {
        formData.append("image", screenshotFile);
      }

      const response = await fetch(`${apiBaseUrl}/verify/screenshot/extract`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Ekran görüntüsünden metin çıkarma başarısız oldu.");
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
    setIsVerifying(true);

    try {
      const response = await fetch(`${apiBaseUrl}/verify/screenshot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildScreenshotVerificationPayload(reviewState, saveReport)),
      });
      if (!response.ok) {
        throw new Error("Gözden geçirilen metinle doğrulama başarısız oldu.");
      }
      const data = await response.json();
      setReport(data);
    } catch (verifyError) {
      setError(verifyError.message);
    } finally {
      setIsVerifying(false);
    }
  }

  async function loadSavedReports() {
    setSavedReportsError("");
    setIsLoadingSavedReports(true);
    try {
      const response = await fetch(`${apiBaseUrl}/reports/saved`);
      if (!response.ok) {
        throw new Error("Kaydedilen raporlar getirilemedi.");
      }
      const payload = await response.json();
      setSavedReports(payload.reports ?? []);
    } catch (loadError) {
      setSavedReportsError(loadError.message);
    } finally {
      setIsLoadingSavedReports(false);
    }
  }

  async function openSavedReport(reportId) {
    setSavedReportsError("");
    try {
      const response = await fetch(`${apiBaseUrl}/reports/saved/${reportId}`);
      if (!response.ok) {
        throw new Error("Kaydedilen rapor açılamadı.");
      }
      const payload = await response.json();
      setReport(payload.report);
    } catch (loadError) {
      setSavedReportsError(loadError.message);
    }
  }

  return (
    <main className="workspace">
      <section className="appShell" aria-label="ProofLens analiz paneli">
        <header className="topbar">
          <div className="windowDots" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div>
            <p className="eyebrow">İndekslenen güvenilir kaynaklara göre</p>
            <h1>ProofLens</h1>
          </div>
          <div className="statusPill">MVP doğrulama çalışma alanı</div>
        </header>

        <div className="layoutGrid">
          <aside className="panel inputPanel">
            <div className="panelHeader">
              <p className="eyebrow">Analiz girişi</p>
              <h2>Şüpheli içeriği kontrol et</h2>
            </div>

            <fieldset className="segmentedControl">
              <legend>Senaryo ailesi</legend>
              {controls.scenarioOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={scenarioFamily === option.value ? "segment active" : "segment"}
                  onClick={() => onScenarioChange(option.value)}
                >
                  {option.label}
                </button>
              ))}
            </fieldset>

            {controls.shouldShowUniversitySelect ? (
              <label className="fieldLabel" htmlFor="university">
                Üniversite
                <select
                  id="university"
                  value={effectiveUniversity ?? "GIBTU"}
                  onChange={(event) => onUniversityChange(event.target.value)}
                >
                  {controls.universityOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}

            <fieldset className="segmentedControl compact">
              <legend>Giriş tipi</legend>
              <button
                type="button"
                className={inputMode === "pasted_text" ? "segment active" : "segment"}
                onClick={() => {
                  setInputMode("pasted_text");
                  resetAnalysisState();
                }}
              >
                Metin yapıştır
              </button>
              <button
                type="button"
                className={inputMode === "screenshot" ? "segment active" : "segment"}
                onClick={() => {
                  setInputMode("screenshot");
                  resetAnalysisState();
                }}
              >
                Screenshot yükle
              </button>
            </fieldset>

            <label className="fieldLabel" htmlFor="demo-case-id">
              Demo vaka
              <select id="demo-case-id" value={selectedDemoCaseId} onChange={(event) => onDemoCaseChange(event.target.value)}>
                <option value="">Demo seçmeden devam et</option>
                {availableDemoCases.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.title}
                  </option>
                ))}
              </select>
            </label>

            {inputMode === "pasted_text" ? (
              <form className="inputStack" onSubmit={onSubmitPastedText}>
                <label className="fieldLabel" htmlFor="claim-text">
                  Şüpheli metin
                  <textarea
                    id="claim-text"
                    value={text}
                    onChange={(event) => setText(event.target.value)}
                    rows={9}
                    placeholder="Duyuru veya ilan metnini buraya yapıştır"
                  />
                </label>
                <button className="primaryButton" type="submit" disabled={isVerifying || text.trim().length === 0}>
                  {isVerifying ? "Kontrol ediliyor" : "Metni doğrula"}
                </button>
                <label className="checkboxRow" htmlFor="save-report-pasted">
                  <input
                    id="save-report-pasted"
                    type="checkbox"
                    checked={saveReport}
                    onChange={(event) => setSaveReport(event.target.checked)}
                  />
                  <span>Doğrulamadan sonra raporu kaydet</span>
                </label>
              </form>
            ) : (
              <form className="inputStack" onSubmit={onExtractScreenshot}>
                <label className="uploadBox" htmlFor="screenshot-upload">
                  <span className="uploadIcon" aria-hidden="true">
                    ↑
                  </span>
                  <span>Ekran görüntüsü yükle</span>
                  <small>{selectedDemoCaseId ? "Demo screenshot seçiliyken dosya gerekmez" : "PNG veya JPG dosyası seç"}</small>
                  <input
                    id="screenshot-upload"
                    type="file"
                    accept="image/*"
                    disabled={Boolean(selectedDemoCaseId)}
                    onChange={(event) => {
                      const file = event.target.files?.[0] ?? null;
                      setScreenshotFile(file);
                      setReviewState(null);
                      setReport(null);
                    }}
                  />
                </label>
                <button className="primaryButton" type="submit" disabled={isExtracting}>
                  {isExtracting ? "Metin okunuyor" : "Metni çıkar ve gözden geçir"}
                </button>
              </form>
            )}

            {error ? <p className="errorMessage">{error}</p> : null}
          </aside>

          <section className="panel workspacePanel">
            <div className="timeline" aria-label="Doğrulama zaman çizelgesi">
              {timeline.map((step) => (
                <div key={step.label} className={`timelineStep ${step.status}`}>
                  <span />
                  <p>{step.label}</p>
                </div>
              ))}
            </div>

            {inputMode === "screenshot" ? (
              <ScreenshotReviewPanel
                selectedDemoCase={selectedDemoCase}
                screenshotPreviewUrl={screenshotPreviewUrl}
                reviewState={reviewState}
                isVerifying={isVerifying}
                saveReport={saveReport}
                onVerifyReviewedScreenshot={onVerifyReviewedScreenshot}
                onSaveReportChange={setSaveReport}
                onReviewTextChange={(nextText) => {
                  if (reviewState) {
                    setReviewState(updateReviewedText(reviewState, nextText));
                  }
                }}
              />
            ) : null}

            {reportModel ? <TruthReportView model={reportModel} /> : <EmptyReportState inputMode={inputMode} />}

            <section className="savedReportsPanel" aria-label="Kaydedilen raporlar">
              <div className="savedReportsHeader">
                <h3>Kaydedilen raporlar</h3>
                <button className="secondaryButton" type="button" onClick={loadSavedReports} disabled={isLoadingSavedReports}>
                  {isLoadingSavedReports ? "Yükleniyor" : "Listeyi yenile"}
                </button>
              </div>
              {savedReportsError ? <p className="errorMessage">{savedReportsError}</p> : null}
              {savedReports.length > 0 ? (
                <div className="savedReportList">
                  {savedReports.map((item) => (
                    <button key={item.id} type="button" className="savedReportRow" onClick={() => openSavedReport(item.id)}>
                      <strong>#{item.id}</strong>
                      <span>{item.overall_verdict}</span>
                      <span>{item.scenario_family}</span>
                      <span>{item.created_at}</span>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="reportSummary">Henüz kaydedilen rapor yok.</p>
              )}
            </section>
          </section>
        </div>
      </section>

      <style jsx global>{`
        * {
          box-sizing: border-box;
        }

        body {
          margin: 0;
          background:
            radial-gradient(circle at top left, rgba(20, 184, 166, 0.16), transparent 28rem),
            linear-gradient(135deg, #111827 0%, #161b22 48%, #1f2933 100%);
          color: #e5eef5;
          font-family:
            Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        button,
        input,
        select,
        textarea {
          font: inherit;
        }

        .workspace {
          min-height: 100vh;
          padding: 28px;
        }

        .appShell {
          width: min(1440px, 100%);
          min-height: calc(100vh - 56px);
          margin: 0 auto;
          overflow: hidden;
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 24px;
          background: rgba(15, 23, 42, 0.82);
          box-shadow: 0 24px 80px rgba(0, 0, 0, 0.38);
          backdrop-filter: blur(18px);
        }

        .topbar {
          display: grid;
          grid-template-columns: auto minmax(0, 1fr) auto;
          gap: 18px;
          align-items: center;
          padding: 18px 22px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.16);
          background: rgba(2, 6, 23, 0.38);
        }

        .windowDots {
          display: flex;
          gap: 8px;
        }

        .windowDots span {
          width: 12px;
          height: 12px;
          border-radius: 999px;
          background: #ef4444;
        }

        .windowDots span:nth-child(2) {
          background: #f59e0b;
        }

        .windowDots span:nth-child(3) {
          background: #10b981;
        }

        h1,
        h2,
        h3,
        p {
          margin: 0;
        }

        h1 {
          font-size: 24px;
          line-height: 1.1;
          letter-spacing: 0;
        }

        h2 {
          font-size: 18px;
          line-height: 1.25;
          letter-spacing: 0;
        }

        h3 {
          font-size: 15px;
          line-height: 1.35;
          letter-spacing: 0;
        }

        .eyebrow {
          color: #67e8f9;
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0;
        }

        .statusPill,
        .badge,
        .summaryChip {
          border: 1px solid rgba(148, 163, 184, 0.22);
          border-radius: 999px;
          background: rgba(15, 23, 42, 0.72);
          color: #cbd5e1;
          font-size: 12px;
          font-weight: 700;
          line-height: 1;
          padding: 8px 10px;
          white-space: nowrap;
        }

        .layoutGrid {
          display: grid;
          grid-template-columns: minmax(320px, 390px) minmax(0, 1fr);
          gap: 18px;
          padding: 18px;
        }

        .panel {
          min-width: 0;
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 16px;
          background: rgba(15, 23, 42, 0.62);
        }

        .inputPanel {
          display: flex;
          flex-direction: column;
          gap: 18px;
          padding: 18px;
        }

        .workspacePanel {
          display: flex;
          flex-direction: column;
          gap: 18px;
          padding: 18px;
        }

        .panelHeader {
          display: grid;
          gap: 6px;
        }

        .segmentedControl {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          min-width: 0;
          margin: 0;
          padding: 0;
          border: 0;
        }

        .segmentedControl legend {
          grid-column: 1 / -1;
          margin-bottom: 2px;
          color: #94a3b8;
          font-size: 12px;
          font-weight: 700;
        }

        .segment,
        .primaryButton {
          min-height: 42px;
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 10px;
          cursor: pointer;
          color: #cbd5e1;
          background: rgba(30, 41, 59, 0.72);
        }

        .segment.active,
        .primaryButton {
          border-color: rgba(45, 212, 191, 0.78);
          color: #ecfeff;
          background: linear-gradient(135deg, rgba(13, 148, 136, 0.92), rgba(8, 145, 178, 0.82));
        }

        .primaryButton {
          width: 100%;
          font-weight: 800;
        }

        .secondaryButton {
          min-height: 36px;
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 10px;
          cursor: pointer;
          color: #e2e8f0;
          background: rgba(30, 41, 59, 0.72);
          padding: 0 10px;
          font-size: 12px;
          font-weight: 700;
        }

        .primaryButton:disabled,
        .segment:disabled,
        .secondaryButton:disabled {
          cursor: not-allowed;
          opacity: 0.62;
        }

        .fieldLabel,
        .inputStack {
          display: grid;
          gap: 8px;
          color: #cbd5e1;
          font-size: 13px;
          font-weight: 700;
        }

        select,
        textarea {
          width: 100%;
          border: 1px solid rgba(148, 163, 184, 0.2);
          border-radius: 10px;
          outline: none;
          color: #f8fafc;
          background: rgba(2, 6, 23, 0.55);
        }

        select {
          height: 42px;
          padding: 0 12px;
        }

        textarea {
          min-height: 154px;
          resize: vertical;
          padding: 12px;
          line-height: 1.45;
        }

        textarea:focus,
        select:focus {
          border-color: rgba(45, 212, 191, 0.84);
          box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.14);
        }

        .uploadBox {
          position: relative;
          display: grid;
          gap: 8px;
          place-items: center;
          min-height: 160px;
          border: 1px dashed rgba(45, 212, 191, 0.45);
          border-radius: 14px;
          color: #dbeafe;
          background: rgba(8, 47, 73, 0.22);
          text-align: center;
          cursor: pointer;
        }

        .uploadBox small {
          color: #94a3b8;
        }

        .uploadBox input {
          position: absolute;
          inset: 0;
          opacity: 0;
          cursor: pointer;
        }

        .uploadBox input:disabled {
          cursor: not-allowed;
        }

        .uploadIcon {
          display: grid;
          place-items: center;
          width: 34px;
          height: 34px;
          border-radius: 999px;
          background: rgba(20, 184, 166, 0.18);
          color: #67e8f9;
          font-size: 20px;
        }

        .errorMessage {
          border: 1px solid rgba(251, 113, 133, 0.35);
          border-radius: 10px;
          padding: 10px 12px;
          color: #fecdd3;
          background: rgba(127, 29, 29, 0.22);
          font-size: 13px;
        }

        .checkboxRow {
          display: flex;
          gap: 8px;
          align-items: center;
          color: #cbd5e1;
          font-size: 13px;
          font-weight: 600;
        }

        .checkboxRow input {
          width: 16px;
          height: 16px;
        }

        .timeline {
          display: grid;
          grid-template-columns: repeat(5, minmax(0, 1fr));
          gap: 8px;
        }

        .timelineStep {
          display: grid;
          grid-template-columns: auto minmax(0, 1fr);
          gap: 8px;
          align-items: center;
          min-height: 44px;
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 10px;
          padding: 9px;
          color: #94a3b8;
          background: rgba(15, 23, 42, 0.58);
          font-size: 12px;
          font-weight: 700;
        }

        .timelineStep span {
          width: 9px;
          height: 9px;
          border-radius: 999px;
          background: #64748b;
        }

        .timelineStep.active {
          color: #cffafe;
          border-color: rgba(45, 212, 191, 0.42);
        }

        .timelineStep.active span,
        .timelineStep.complete span {
          background: #14b8a6;
          box-shadow: 0 0 0 4px rgba(20, 184, 166, 0.12);
        }

        .timelineStep.complete {
          color: #bbf7d0;
        }

        .reviewPanel,
        .reportShell,
        .emptyReport,
        .savedReportsPanel {
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 14px;
          background: rgba(2, 6, 23, 0.24);
        }

        .reviewPanel {
          display: grid;
          grid-template-columns: minmax(220px, 0.7fr) minmax(0, 1fr);
          gap: 14px;
          padding: 14px;
        }

        .screenshotPreview {
          min-height: 230px;
          overflow: hidden;
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 12px;
          background: #e5e7eb;
          color: #111827;
        }

        .screenshotPreview img {
          width: 100%;
          height: 100%;
          min-height: 230px;
          object-fit: cover;
          display: block;
        }

        .fauxScreenshot {
          display: grid;
          gap: 12px;
          padding: 18px;
          min-height: 230px;
          align-content: start;
        }

        .fauxScreenshot strong {
          font-size: 15px;
        }

        .fauxScreenshot p {
          font-size: 14px;
          line-height: 1.5;
        }

        .reviewForm {
          display: grid;
          gap: 12px;
        }

        .reportShell {
          overflow: hidden;
        }

        .reportHeader {
          display: grid;
          gap: 14px;
          padding: 18px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.14);
          background: rgba(30, 41, 59, 0.48);
        }

        .verdictRow {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          align-items: center;
          justify-content: space-between;
        }

        .overallVerdict {
          display: grid;
          gap: 4px;
        }

        .overallVerdict strong {
          color: #fef3c7;
          font-size: 34px;
          line-height: 1;
        }

        .summaryStrip {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .summaryChip.source,
        .badge.source {
          border-color: rgba(52, 211, 153, 0.34);
          color: #bbf7d0;
          background: rgba(6, 78, 59, 0.24);
        }

        .summaryChip.risk,
        .badge.risk {
          border-color: rgba(251, 191, 36, 0.38);
          color: #fde68a;
          background: rgba(120, 53, 15, 0.26);
        }

        .reportBody {
          display: grid;
          gap: 16px;
          padding: 18px;
        }

        .claimCard {
          display: grid;
          gap: 14px;
          border: 1px solid rgba(148, 163, 184, 0.18);
          border-radius: 10px;
          padding: 16px;
          background: rgba(15, 23, 42, 0.66);
        }

        .claimTopline {
          display: grid;
          grid-template-columns: minmax(0, 1fr) auto;
          gap: 12px;
          align-items: start;
        }

        .claimText {
          margin-top: 6px;
          color: #f8fafc;
          line-height: 1.45;
        }

        .verdictBadge {
          border-radius: 999px;
          padding: 8px 10px;
          color: #fff7ed;
          background: rgba(245, 158, 11, 0.2);
          font-size: 12px;
          font-weight: 800;
          white-space: nowrap;
        }

        .claimExplanation,
        .reportSummary,
        .emptyReport p {
          color: #cbd5e1;
          line-height: 1.55;
          font-size: 14px;
        }

        .badgeRow,
        .actionList,
        .signalList {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .evidenceColumns {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 14px;
          border-top: 1px solid rgba(148, 163, 184, 0.12);
          padding-top: 14px;
        }

        .evidenceSection {
          display: grid;
          gap: 8px;
        }

        .evidenceSection h4,
        .sourceRail h4,
        .riskActionGrid h4 {
          margin: 0;
          color: #e2e8f0;
          font-size: 13px;
          letter-spacing: 0;
        }

        .evidenceSection p,
        .sourceRow p {
          color: #cbd5e1;
          font-size: 13px;
          line-height: 1.5;
        }

        .sourceRail {
          display: grid;
          gap: 10px;
          border-top: 1px solid rgba(148, 163, 184, 0.12);
          padding-top: 14px;
        }

        .sourceRow {
          display: grid;
          gap: 5px;
          padding: 0 0 10px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        }

        .sourceRow:last-child {
          border-bottom: 0;
          padding-bottom: 0;
        }

        .sourceRow a {
          color: #67e8f9;
          text-decoration: none;
          word-break: break-word;
        }

        .riskActionGrid {
          display: grid;
          grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
          gap: 14px;
          border-top: 1px solid rgba(148, 163, 184, 0.12);
          padding-top: 14px;
        }

        .actionList {
          display: grid;
        }

        .actionItem {
          border-left: 3px solid #14b8a6;
          padding: 8px 10px;
          border-radius: 6px;
          color: #ecfeff;
          background: rgba(20, 184, 166, 0.1);
          font-size: 13px;
          line-height: 1.45;
        }

        .emptyReport {
          display: grid;
          gap: 10px;
          min-height: 300px;
          align-content: center;
          justify-items: center;
          padding: 32px;
          text-align: center;
        }

        @media (max-width: 980px) {
          .workspace {
            padding: 12px;
          }

          .appShell {
            min-height: calc(100vh - 24px);
            border-radius: 18px;
          }

          .topbar {
            grid-template-columns: auto minmax(0, 1fr);
          }

          .statusPill {
            grid-column: 1 / -1;
            justify-self: start;
          }

          .layoutGrid,
          .reviewPanel,
          .evidenceColumns,
          .riskActionGrid {
            grid-template-columns: 1fr;
          }

          .timeline {
            grid-template-columns: 1fr;
          }

          .claimTopline {
            grid-template-columns: 1fr;
          }
        }

        .savedReportsPanel {
          display: grid;
          gap: 10px;
          padding: 14px;
        }

        .savedReportsHeader {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 10px;
        }

        .savedReportList {
          display: grid;
          gap: 8px;
        }

        .savedReportRow {
          display: grid;
          grid-template-columns: auto auto minmax(0, 1fr) auto;
          gap: 10px;
          align-items: center;
          border: 1px solid rgba(148, 163, 184, 0.18);
          border-radius: 10px;
          background: rgba(15, 23, 42, 0.62);
          color: #e2e8f0;
          padding: 10px;
          text-align: left;
          cursor: pointer;
        }
      `}</style>
    </main>
  );
}

function ScreenshotReviewPanel({
  selectedDemoCase,
  screenshotPreviewUrl,
  reviewState,
  isVerifying,
  saveReport,
  onVerifyReviewedScreenshot,
  onSaveReportChange,
  onReviewTextChange,
}) {
  const previewTitle = selectedDemoCase?.title ?? "Yüklenen screenshot";
  const previewText = reviewState?.reviewedText || selectedDemoCase?.text || "Screenshot seçildiğinde önizleme burada görünür.";

  return (
    <section className="reviewPanel" aria-label="Ekrandan okunan metin">
      <div className="screenshotPreview">
        {screenshotPreviewUrl ? (
          <img src={screenshotPreviewUrl} alt="Yüklenen screenshot önizlemesi" />
        ) : (
          <div className="fauxScreenshot">
            <strong>{previewTitle}</strong>
            <p>{previewText}</p>
          </div>
        )}
      </div>

      <form className="reviewForm" onSubmit={onVerifyReviewedScreenshot}>
        <div className="panelHeader">
          <p className="eyebrow">Extracted Text Review</p>
          <h2>Ekrandan okunan metni gözden geçir</h2>
        </div>
        <label className="fieldLabel" htmlFor="reviewed-text">
          Düzenlenebilir OCR metni
          <textarea
            id="reviewed-text"
            rows={8}
            value={reviewState?.reviewedText ?? ""}
            onChange={(event) => onReviewTextChange(event.target.value)}
            placeholder="Önce screenshot metnini çıkar"
          />
        </label>
        <button className="primaryButton" type="submit" disabled={!reviewState || isVerifying}>
          {isVerifying ? "Rapor hazırlanıyor" : "Gözden geçirilen metinle doğrula"}
        </button>
        <label className="checkboxRow" htmlFor="save-report-screenshot">
          <input
            id="save-report-screenshot"
            type="checkbox"
            checked={saveReport}
            onChange={(event) => onSaveReportChange(event.target.checked)}
          />
          <span>Doğrulamadan sonra raporu kaydet</span>
        </label>
      </form>
    </section>
  );
}

function TruthReportView({ model }) {
  return (
    <article className="reportShell" aria-label="Truth Report">
      <header className="reportHeader">
        <div className="verdictRow">
          <div className="overallVerdict">
            <p className="eyebrow">Genel karar</p>
            <strong>{model.overallVerdict}</strong>
          </div>
          <span className="statusPill">{model.confidenceLevel}</span>
        </div>
        <p className="reportSummary">{model.summaryMessage}</p>
        <div className="summaryStrip">
          {model.summaryStrip.map((item) => (
            <span key={item.label} className={`summaryChip ${item.tone}`}>
              {item.label}
            </span>
          ))}
        </div>
      </header>

      <div className="reportBody">
        {model.claimCards.map((card, index) => (
          <section className="claimCard" key={`${card.claimText}-${index}`}>
            <div className="claimTopline">
              <div>
                <p className="eyebrow">Kontrol edilen iddia</p>
                <h3 className="claimText">{card.claimText}</h3>
              </div>
              <span className="verdictBadge">
                {card.verdict} · {card.confidenceLevel}
              </span>
            </div>
            <p className="claimExplanation">{card.explanation}</p>
            <div className="badgeRow">
              {card.sourceBadges.map((badge) => (
                <span key={badge.label} className={`badge ${badge.tone}`}>
                  {badge.label}
                </span>
              ))}
            </div>
            <div className="evidenceColumns">
              <EvidenceSection title="Destekleyen kanıt" items={card.supportingEvidence} emptyText="Bu iddia için destekleyen kanıt bulunmadı." />
              <EvidenceSection
                title="Çelişen kanıt"
                items={card.contradictingEvidence}
                emptyText="Bu iddia için doğrudan çelişen kanıt bulunmadı."
              />
            </div>
            {card.sourcesChecked.length > 0 ? (
              <SourceRail title="Bu iddia için taranan kaynaklar" sources={card.sourcesChecked} />
            ) : null}
          </section>
        ))}

        <div className="riskActionGrid">
          <section>
            <h4>Manipulation Signals</h4>
            <div className="signalList">
              {model.manipulationSignals.length > 0 ? (
                model.manipulationSignals.map((signal) => (
                  <span key={signal} className="badge risk">
                    {signal}
                  </span>
                ))
              ) : (
                <span className="badge">Risk sinyali yok</span>
              )}
            </div>
          </section>

          <section>
            <h4>Önerilen aksiyonlar</h4>
            <div className="actionList">
              {model.recommendedActions.map((action) => (
                <p key={action} className="actionItem">
                  {action}
                </p>
              ))}
            </div>
          </section>
        </div>

        {model.sourceCitations.length > 0 ? <SourceRail title="Rapor kaynakları" sources={model.sourceCitations} /> : null}
      </div>
    </article>
  );
}

function EvidenceSection({ title, items, emptyText }) {
  return (
    <section className="evidenceSection">
      <h4>{title}</h4>
      {items.length > 0 ? items.map((item) => <p key={`${title}-${item.snippet}`}>{item.snippet}</p>) : <p>{emptyText}</p>}
    </section>
  );
}

function SourceRail({ title, sources }) {
  return (
    <section className="sourceRail">
      <h4>{title}</h4>
      {sources.map((source, index) => (
        <div className="sourceRow" key={`${source.url}-${source.title}-${index}`}>
          <div className="badgeRow">
            <span className="badge source">{source.trustLabel}</span>
            {source.sourceOwner ? <span className="badge">{source.sourceOwner}</span> : null}
            {source.retrievedAt ? <span className="badge">{source.retrievedAt}</span> : null}
          </div>
          <p>{source.title}</p>
          {source.snippet ? <p>{source.snippet}</p> : null}
          {source.url ? (
            <a href={source.url} target="_blank" rel="noreferrer">
              Kaynağı aç
            </a>
          ) : null}
        </div>
      ))}
    </section>
  );
}

function EmptyReportState({ inputMode }) {
  return (
    <section className="emptyReport">
      <p className="eyebrow">Truth Report</p>
      <h2>{inputMode === "screenshot" ? "Önce screenshot metnini çıkar" : "Analize hazır"}</h2>
      <p>Rapor oluştuğunda genel karar, iddia kartları, kaynak rozetleri, risk sinyalleri ve önerilen aksiyonlar burada görünür.</p>
    </section>
  );
}

function buildTimelineState(hasReport, hasReviewState, isWorking) {
  if (hasReport) {
    return VERIFICATION_TIMELINE_STEPS.map((label) => ({ label, status: "complete" }));
  }

  if (isWorking) {
    return VERIFICATION_TIMELINE_STEPS.map((label, index) => ({
      label,
      status: index === 0 ? "active" : "pending",
    }));
  }

  if (hasReviewState) {
    return VERIFICATION_TIMELINE_STEPS.map((label, index) => ({
      label,
      status: index === 0 ? "complete" : index === 1 ? "active" : "pending",
    }));
  }

  return VERIFICATION_TIMELINE_STEPS.map((label) => ({ label, status: "pending" }));
}
