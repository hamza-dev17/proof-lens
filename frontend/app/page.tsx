"use client";

import { useState } from "react";

export default function Page() {
  const [text, setText] = useState("");
  const [report, setReport] = useState(null);
  const [error, setError] = useState("");
  const [scenarioFamily, setScenarioFamily] = useState("university_announcement");

  const selectedUniversity =
    scenarioFamily === "university_announcement" ? "GIBTU" : null;

  async function onSubmit(event) {
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

  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: 24, fontFamily: "ui-sans-serif, system-ui" }}>
      <h1>ProofLens Analyzer (MVP Iskelet)</h1>
      <p>
        Senaryo: {scenarioFamily === "university_announcement" ? "Universite duyurusu" : "Staj/Is dolandiriciligi"}
        {" | "}
        Secili universite: {selectedUniversity ?? "Yok"}
      </p>

      <form onSubmit={onSubmit}>
        <label htmlFor="scenario-family">Senaryo ailesi</label>
        <select
          id="scenario-family"
          value={scenarioFamily}
          onChange={(event) => setScenarioFamily(event.target.value)}
          style={{ display: "block", marginTop: 8, marginBottom: 12 }}
        >
          <option value="university_announcement">Universite duyurusu</option>
          <option value="internship_job_scam">Staj/is dolandiriciligi</option>
        </select>

        <label htmlFor="claim-text">Supheli metin</label>
        <textarea
          id="claim-text"
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={6}
          style={{ width: "100%", marginTop: 8 }}
          placeholder="Duyuru metnini buraya yapistir"
        />
        <button type="submit" style={{ marginTop: 12 }}>Dogrula</button>
      </form>

      {error ? <p>{error}</p> : null}

      {report ? (
        <section style={{ marginTop: 24 }}>
          <h2>Truth Report</h2>
          <p><strong>Genel karar:</strong> {report.overall_verdict}</p>
          <p><strong>Guven seviyesi:</strong> {report.confidence_level}</p>
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
