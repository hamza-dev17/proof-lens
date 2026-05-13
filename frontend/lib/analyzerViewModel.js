export const VERIFICATION_TIMELINE_STEPS = [
  "Metin okunuyor",
  "İddialar ayrılıyor",
  "Resmi kaynaklarda aranıyor",
  "Kanıtlar karşılaştırılıyor",
  "Rapor hazırlanıyor",
];

export const SCENARIO_OPTIONS = [
  { value: "university_announcement", label: "Üniversite duyurusu" },
  { value: "internship_job_scam", label: "Staj / iş ilanı" },
];

export const UNIVERSITY_OPTIONS = [
  { value: "GIBTU", label: "GİBTÜ" },
  { value: "GAZIANTEP", label: "Gaziantep Üniversitesi" },
  { value: "HASAN_KALYONCU", label: "Hasan Kalyoncu Üniversitesi" },
  { value: "SANKO", label: "SANKO Üniversitesi" },
];

const TRUST_LEVEL_LABELS = {
  official: "Resmi kaynak",
  public_guidance: "Güvenilir rehber kaynak",
  synthetic_demo: "Demo kaynak",
};

export function buildAnalyzerControlState(scenarioFamily, selectedUniversity) {
  const shouldShowUniversitySelect = scenarioFamily === "university_announcement";

  return {
    scenarioOptions: SCENARIO_OPTIONS,
    universityOptions: UNIVERSITY_OPTIONS,
    shouldShowUniversitySelect,
    selectedUniversity: shouldShowUniversitySelect ? selectedUniversity || "GIBTU" : null,
  };
}

export function buildAnalyzerViewModel(report) {
  const claimCount = Array.isArray(report.checkable_claims) ? report.checkable_claims.length : 0;
  const sourceCount = Array.isArray(report.source_citations) ? report.source_citations.length : 0;
  const riskSignalCount = Array.isArray(report.manipulation_signals) ? report.manipulation_signals.length : 0;
  const confidenceLevel = report.overall_confidence_level ?? report.confidence_level;
  const claimCards = buildClaimCards(report.claim_cards ?? report.claims ?? []);
  const recommendedActions = Array.isArray(report.recommended_actions) ? report.recommended_actions : [];
  const summaryMessage = report.summary?.tr_message ?? "İndekslenen güvenilir kaynaklara göre rapor hazırlandı.";

  return {
    overallVerdict: report.overall_verdict,
    confidenceLevel,
    claimCount,
    sourceCount,
    riskSignalCount,
    summaryLine: `Genel sonuç: ${report.overall_verdict} (${confidenceLevel})`,
    summaryMessage,
    summaryStrip: [
      { label: `${claimCount} iddia kontrol edildi`, tone: "neutral" },
      { label: `${sourceCount} kaynak tarandı`, tone: "source" },
      { label: `${riskSignalCount} risk sinyali`, tone: "risk" },
    ],
    timelineSteps: VERIFICATION_TIMELINE_STEPS.map((label) => ({ label, status: "complete" })),
    sourceCitations: buildSourceRows(report.source_citations ?? []),
    claimCards,
    manipulationSignals: Array.isArray(report.manipulation_signals) ? report.manipulation_signals : [],
    recommendedActions,
    normalizedTextForDisplay: [
      report.overall_verdict,
      confidenceLevel,
      summaryMessage,
      ...claimCards.flatMap((card) => [
        card.claimText,
        card.verdict,
        card.confidenceLevel,
        card.explanation,
        ...card.supportingEvidence.map((item) => item.snippet),
        ...card.contradictingEvidence.map((item) => item.snippet),
      ]),
      ...recommendedActions,
    ].join(" "),
  };
}

function buildClaimCards(cards) {
  return cards.map((card) => {
    const sourcesChecked = card.sources_checked ?? [];

    return {
      claimText: card.claim_text ?? card.claim ?? "",
      verdict: card.verdict,
      confidenceLevel: card.confidence_level,
      explanation: card.explanation_tr ?? card.explanation ?? "",
      supportingEvidence: normalizeEvidence(card.supporting_evidence),
      contradictingEvidence: normalizeEvidence(card.contradicting_evidence),
      sourcesChecked: buildSourceRows(sourcesChecked),
      sourceBadges: buildSourceBadges(sourcesChecked[0]),
    };
  });
}

function normalizeEvidence(items) {
  if (!Array.isArray(items)) {
    return [];
  }

  return items.map((item) => ({
    snippet: item.snippet ?? item.text ?? "",
    chunkId: item.chunk_id ?? null,
  }));
}

function buildSourceRows(sources) {
  return sources.map((source) => ({
    title: source.title ?? "Kaynak",
    sourceOwner: source.source_owner ?? "",
    trustLevel: source.trust_level ?? "",
    trustLabel: TRUST_LEVEL_LABELS[source.trust_level] ?? source.trust_level ?? "Kaynak",
    url: source.url ?? "",
    retrievedAt: source.retrieved_at ?? "",
    snippet: source.snippet ?? "",
  }));
}

function buildSourceBadges(source) {
  if (!source) {
    return [];
  }

  return [
    { label: TRUST_LEVEL_LABELS[source.trust_level] ?? source.trust_level ?? "Kaynak", tone: "source" },
    { label: source.source_owner ?? "Kaynak sahibi", tone: "neutral" },
    { label: source.retrieved_at ?? "Tarih yok", tone: "neutral" },
  ];
}
