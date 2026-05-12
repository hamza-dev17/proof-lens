export function buildAnalyzerViewModel(report) {
  const claimCount = Array.isArray(report.checkable_claims) ? report.checkable_claims.length : 0;
  const sourceCount = Array.isArray(report.source_citations) ? report.source_citations.length : 0;
  const riskSignalCount = Array.isArray(report.manipulation_signals) ? report.manipulation_signals.length : 0;

  return {
    overallVerdict: report.overall_verdict,
    confidenceLevel: report.confidence_level,
    claimCount,
    sourceCount,
    riskSignalCount,
    summaryLine: `Genel sonuc: ${report.overall_verdict} (${report.confidence_level})`,
  };
}
