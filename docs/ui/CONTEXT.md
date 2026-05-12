# ProofLens UI Context

The ProofLens UI must help judges understand the product in seconds: what the user submitted, which trusted sources were checked, what verdict was reached, and what action the user should take next. The interface is Turkish-first, student-friendly, and built around the actual verification workflow rather than a marketing landing page.

## Five UI Recommendations

**1. Start With The Verification Tool**

The first screen should be the usable ProofLens analyzer, not a landing page. Judges should immediately see scenario selection, university selection when relevant, screenshot upload, text paste, and prepared demo cases.

Recommended first-screen structure:

- top bar with `ProofLens`
- scenario selector: `Üniversite duyurusu` and `Staj / iş ilanı`
- university selector for the university lane
- upload area and paste-text area
- three demo case shortcuts

**2. Make Trust Visible**

The UI should constantly remind users that verdicts are based on indexed trusted sources, not model memory. Evidence cards should show source title, source owner, trust level, original URL, retrieval date, and a short snippet.

Recommended copy:

- `İndekslenen güvenilir kaynaklara göre`
- `Resmi kaynak`
- `Güvenilir rehber kaynak`
- `Demo kaynak`

**3. Use A Clear Report Hierarchy**

The final report should be easy to scan under presentation pressure. Put the conservative overall verdict first, then per-claim cards, then evidence, manipulation signals, and recommended actions.

Recommended report order:

1. Overall verdict and confidence level
2. One-sentence summary
3. Claim cards
4. Evidence sources checked
5. Manipulation signals
6. Recommended actions

Verdict labels:

- `Doğru`
- `Yanlış`
- `Yanıltıcı`
- `Doğrulanamadı`

Confidence labels:

- `Yüksek güven`
- `Orta güven`
- `Düşük güven`

**4. Separate Evidence From Risk Signals**

Manipulation signals should look visually different from verdict evidence. A scammy phrase is a warning sign, not proof by itself.

Recommended UI split:

- evidence area: official sources, snippets, supporting/contradicting evidence
- risk area: urgent language, payment request, anonymous authority, missing date, no official source
- action area: what the student should do next

This protects the product from overclaiming and makes the reasoning easier to defend to judges.

**5. Show The Process Without Raw Agent Chatter**

The app should feel transparent, but not expose messy internal reasoning. Show extracted text review and a short progress timeline instead.

Required interaction:

- image upload shows `Ekrandan okunan metin`
- user can edit OCR text before analysis
- progress timeline shows:
  - `Metin okunuyor`
  - `İddialar ayrılıyor`
  - `Resmi kaynaklarda aranıyor`
  - `Kanıtlar karşılaştırılıyor`
  - `Rapor hazırlanıyor`

Avoid showing raw agent messages, chain-of-thought style text, or long technical logs in the normal UI.

## Visual Direction

ProofLens should feel like a modern student safety and verification tool: calm, credible, fast to scan, and not overly decorative.

- Use restrained colors with strong verdict accents.
- Use icons for upload, paste, source link, warning, verdict, and save actions.
- Keep cards compact and scannable.
- Avoid a heavy marketing hero.
- Avoid exact confidence percentages in the main UI.
- Keep all normal interface text in Turkish.

## Modern Minimal Design Standard

Minimalistic does not mean empty. The UI should feel premium, deliberate, and evidence-driven. Judges should understand in the first 10 seconds that ProofLens is not a chatbot: it is a structured verification tool.

Recommended desktop composition:

- left panel: input type, scenario selection, university selection, upload/paste area, demo cases
- right panel: extracted text review, progress timeline, or final truth report
- bottom or side rail: trusted sources checked
- report header: overall verdict plus a compact summary strip
- input area: uploaded/synthetic screenshot preview when available

Recommended visual style:

- dark MacBook-style graphite background
- app framed like a premium desktop verification workspace
- subtle translucent dark panels with crisp borders
- one strong cyan/teal accent for primary actions
- verdict colors used only where they carry meaning
- compact cards with clear headings and short body text
- lucide-style icons in buttons and source rows
- subtle loading/progress states, no flashy animation

Verdict color system:

- `Doğru`: green/emerald accent
- `Yanlış`: red/rose accent
- `Yanıltıcı`: amber/orange accent
- `Doğrulanamadı`: neutral gray accent
- manipulation signals: amber warning styling, visually separate from verdicts

Typography:

- use a clean sans-serif font
- large type only for the overall verdict and main page title
- claim cards should use compact headings, not hero-sized text
- avoid dense paragraphs; prefer one-sentence explanations and expandable details

Judge persuasion moments:

1. The first screen immediately looks usable, not like a pitch deck.
2. The user can upload a screenshot and see OCR text before analysis.
3. The report shows official sources with links and retrieval dates.
4. The verdict is visually obvious but still conservative.
5. The recommended action tells the student exactly what to do next.
6. The summary strip quickly shows how much work the system did.

Avoid:

- oversized marketing hero sections
- decorative gradients or abstract blobs
- murky dark styling that hides evidence
- raw agent logs
- fake precision such as `%87 güven`
- crowded cards with too many badges

## Dark MacBook Preview Direction

The preferred judge-facing dashboard direction is a dark MacBook-inspired analyzer:

- rounded desktop-app shell with macOS-style window controls
- graphite panels, not pure black
- cyan/teal primary action color
- emerald for completed progress and trusted sources
- amber for suspicious or misleading signals
- rose for false/contradicted claims
- neutral gray for unverified claims
- screenshot preview card for the suspicious input
- compact report summary chips such as `3 iddia kontrol edildi`, `2 resmi kaynak tarandı`, and `3 risk sinyali`
- premium source badges such as `Resmi kaynak`, institution name, and retrieval date
- stronger overall verdict header with subtle amber emphasis when the report is suspicious
- tighter inner card radius than the outer desktop shell

The dark theme must keep evidence legible. Source titles, snippets, verdict labels, and recommended actions should have stronger contrast than decorative UI chrome.

## Judge Demo Priorities

For presentation, optimize the UI around three prepared demo cases:

- fake GİBTÜ exam cancellation
- fake GİBTÜ internship/payment announcement
- internship scam post with registration fee

Each demo case should have a text version and screenshot version so the team can demonstrate both reliable text analysis and the vision/OCR path.
