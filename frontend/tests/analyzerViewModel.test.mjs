import test from "node:test";
import assert from "node:assert/strict";

import { buildAnalyzerControlState, buildAnalyzerViewModel } from "../lib/analyzerViewModel.js";

const fixtureReport = {
  overall_verdict: "Dogrulanamadi",
  confidence_level: "Dusuk guven",
  checkable_claims: ["GIBTU final sinavlari iptal edildi"],
  claim_cards: [
    {
      claim_text: "GIBTU final sinavlari iptal edildi",
      verdict: "Dogrulanamadi",
      confidence_level: "Dusuk guven",
      explanation_tr: "Resmi kaynaklarda dogrudan destek bulunamadi.",
    },
  ],
  source_citations: [
    {
      title: "GIBTU Akademik Takvimler",
      source_owner: "GIBTU Ogrenci Isleri Daire Baskanligi",
      trust_level: "official",
      url: "https://www.gibtu.edu.tr/ogrenciisleri/icerik/31231/akademik-takvimler",
      retrieved_at: "2026-05-12",
    },
  ],
  manipulation_signals: ["Acil ve kesin ifade dili"],
  recommended_actions: ["Odeme yapmadan once resmi duyuruyu kontrol et."],
};

test("buildAnalyzerViewModel provides minimal renderable analyzer fields", () => {
  const model = buildAnalyzerViewModel(fixtureReport);

  assert.equal(model.overallVerdict, "Dogrulanamadi");
  assert.equal(model.confidenceLevel, "Dusuk guven");
  assert.equal(model.claimCount, 1);
  assert.equal(model.sourceCount, 1);
  assert.equal(model.riskSignalCount, 1);
  assert.match(model.summaryLine, /Dogrulanamadi/);
});

test("buildAnalyzerViewModel exposes a complete polished truth report without fake precision", () => {
  const model = buildAnalyzerViewModel({
    ...fixtureReport,
    confidence_percentage: 87,
    claim_cards: [
      {
        ...fixtureReport.claim_cards[0],
        supporting_evidence: [{ snippet: "Akademik takvimde final haftasi yer aliyor." }],
        contradicting_evidence: [{ snippet: "Iptal edildi bilgisi yer almiyor." }],
        sources_checked: [
          {
            title: "GIBTU Akademik Takvimler",
            source_owner: "GIBTU Ogrenci Isleri",
            trust_level: "official",
            url: "https://www.gibtu.edu.tr/ogrenciisleri/icerik/31231/akademik-takvimler",
            retrieved_at: "2026-05-12",
            snippet: "Final sinavlari akademik takvimde yayinlanan tarihlerde yapilir.",
          },
        ],
      },
    ],
  });

  assert.deepEqual(
    model.timelineSteps.map((step) => step.label),
    [
      "Metin okunuyor",
      "İddialar ayrılıyor",
      "Resmi kaynaklarda aranıyor",
      "Kanıtlar karşılaştırılıyor",
      "Rapor hazırlanıyor",
    ],
  );
  assert.deepEqual(model.summaryStrip, [
    { label: "1 iddia kontrol edildi", tone: "neutral" },
    { label: "1 kaynak tarandı", tone: "source" },
    { label: "1 risk sinyali", tone: "risk" },
  ]);
  assert.equal(model.claimCards[0].sourceBadges[0].label, "Resmi kaynak");
  assert.equal(model.claimCards[0].sourceBadges[1].label, "GIBTU Ogrenci Isleri");
  assert.equal(model.claimCards[0].sourceBadges[2].label, "2026-05-12");
  assert.equal(model.claimCards[0].supportingEvidence[0].snippet, "Akademik takvimde final haftasi yer aliyor.");
  assert.equal(model.claimCards[0].contradictingEvidence[0].snippet, "Iptal edildi bilgisi yer almiyor.");
  assert.deepEqual(model.recommendedActions, ["Odeme yapmadan once resmi duyuruyu kontrol et."]);
  assert.doesNotMatch(model.normalizedTextForDisplay, /%|87/);
});

test("buildAnalyzerControlState renders university selection only for the university scenario", () => {
  const universityState = buildAnalyzerControlState("university_announcement", "GAZIANTEP");
  const internshipState = buildAnalyzerControlState("internship_job_scam", "GIBTU");

  assert.equal(universityState.shouldShowUniversitySelect, true);
  assert.equal(universityState.selectedUniversity, "GAZIANTEP");
  assert.deepEqual(
    universityState.universityOptions.map((option) => option.label),
    ["GİBTÜ", "Gaziantep Üniversitesi", "Hasan Kalyoncu Üniversitesi", "SANKO Üniversitesi"],
  );

  assert.equal(internshipState.shouldShowUniversitySelect, false);
  assert.equal(internshipState.selectedUniversity, null);
});
