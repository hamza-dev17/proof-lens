import test from "node:test";
import assert from "node:assert/strict";

import { buildAnalyzerViewModel } from "../lib/analyzerViewModel.js";

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
