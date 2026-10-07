/ponytail
/caveman

Same token rules, mandatory skills (impeccable, gpt-taste, emil-kowalski, ui-ux-pro-max, frontend-design) and Playwright MCP rules as the main build. No AI slop. The legal pages must match the app's existing design tokens and look hand-made. Plan in 10 lines max, then build.

TASK
Add all legal content and UX to the app: a Legal page, a first-use consent gate, and single-sourced disclaimer copy. Frontend only. No real API calls. Do not touch the teammate's backend files.

IMPORTANT: HONESTY RULE
Legal text must be TRUE to how the app actually works. Never claim "never stored", "deleted" or "no data leaves your device" unless it is verified for that mode.
- Demo Mode: nothing is sent anywhere.
- Real mode: the image and extracted text go to third-party AI providers (Google Gemini for OCR, Groq for chat; confirm with the backend). Those providers process data under their own terms. Free-tier terms may let a provider retain or use inputs, so check their current terms via web search and word the text accordingly.
- Our side: processed in memory, no database, no accounts. Word it as "we do not store it on our servers", not as a guarantee about providers.
Anything unknown becomes a visible placeholder (see PLACEHOLDERS), never an invented fact.

LEGAL DOCUMENTS TO DRAFT
Store each as legal/<name>.md (so a lawyer or teammate can edit it without touching code). Each document starts with a 3-5 bullet "In plain English" summary, then the full text. Plain language, short sentences, no wall of legalese. Header shows Version and Last updated (constants in legal_config.py), and a "Prototype built for a hackathon" notice.
1. Terms of Use: what the app is (an educational prescription-literacy tool); eligibility 18+ (under-18s need a parent or guardian to use it); user may upload only their own prescription or one they are authorised to use; acceptable use; no medical-device, diagnosis or treatment function; accuracy limits of OCR and AI, including look-alike drug names; user must verify every extracted item; no guarantees ("as is"); limitation of liability; intellectual property; changes to terms; termination; severability; governing law India and jurisdiction [CITY]; contact.
2. Privacy Notice: aligned with India's DPDP Act 2023. Cover what is collected (prescription image, extracted medicine text, chat messages, basic session data), the purpose limited to extracting and explaining this prescription only, legal basis (consent), who processes it (named third-party providers, placeholders if unconfirmed), retention (session only on our side), user rights (access, correction, erasure, withdraw consent, grievance redressal, nominate), children's data, security measures, cross-border processing by providers, breach handling, grievance officer details (placeholders), and updates. Prescriptions are health data, so use a "sensitive" tone. Use web search (MeitY or official gazette sources) to verify the current status and commencement of the DPDP Act and Rules as of today, and which older rules still apply (for example the IT SPDI Rules 2011). Phrase carefully, never overclaim compliance, and use "designed to align with".
3. Medical Disclaimer: not a doctor, no doctor-patient relationship, not diagnosis or treatment advice, never change dose or stop medication based on this app, always confirm with a doctor or pharmacist, the app can make mistakes, and for emergencies call 112 or the local emergency number.
4. AI and Third-Party Processing Disclosure: which AI does what (extract vs explain), what is sent to each, hallucination and misread risk, and why the human verification step exists.
5. Your Rights and Grievance Redressal: how to ask for access, correction or erasure, how to withdraw consent (in-app: "Reset session"), the grievance officer, and a response timeline placeholder.
6. Acknowledgements and Licenses: read the ACTUAL licenses from installed packages (streamlit, pandas, pillow, fonts) with a command, do not guess. Add a note that illustrations were AI-generated.
Also: a Cookies/Storage note only if the app actually sets any (check). Otherwise one line saying none are used.

PLACEHOLDERS
Put every unknown in legal_config.py as a named constant: ENTITY_NAME, CONTACT_EMAIL, GRIEVANCE_OFFICER_NAME, GRIEVANCE_EMAIL, JURISDICTION_CITY, HOSTING_PROVIDER, and so on. Never invent names, emails or addresses. Add a dev check (script or app startup warning) that lists every placeholder still unresolved. At the end, show me that list so I can fill it in.

UX TO BUILD
1. Legal page: reached from a persistent footer ("Terms · Privacy · Medical disclaimer · Legal") and from the sidebar. Implement as a view toggle in session_state (view = 'app' | 'legal') that does NOT reset step, verified data or chat. "Back to app" returns to the exact step. Layout: left table of contents (becomes a top selector on mobile) plus the document in a comfortable reading column (65-75 characters wide), good type hierarchy, anchored headings, and print-friendly CSS. Optional ?page=legal deep link.
2. Consent gate on Step 1: a clear card before the uploader. Uploads are disabled until consent is given. Requirements: no pre-ticked boxes; two SEPARATE checkboxes, (a) "I have read the Terms and Medical Disclaimer and I am 18+ (or using this with a parent or guardian)" and (b) "I consent to my prescription image and extracted text being processed by [named providers] only to read and explain this prescription". The wording of (b) adapts to Demo Mode ("In Demo Mode nothing leaves your device"). Links open the Legal page without losing state. Consent is kept only in session_state (no storage, which fits the no-persistence claim), with a timestamp for display. Withdrawal is one click ("Reset session"), which clears all data and consent. Note in HANDOFF.md that a production version needs a durable consent record.
3. Single-sourced copy: the short disclaimer (sidebar, report footer, consent card, chat header) is ONE constant in legal_config.py used everywhere. No duplicated wording.
4. Chat guard rail: a small non-dismissible line near the chat input ("Educational only. Not medical advice."). Include an emergency line in the report footer.
5. All states: consent not given (uploader disabled and says why), consent given, the legal page in desktop and mobile, long-document scroll, and a missing-file error state.

DESIGN
Reuse the existing tokens. Legal pages are read, not scanned: generous line height, calm hierarchy, subtle section dividers, no cards-on-cards, and no accordions for core text. The consent card should feel serious and clear, not like a cookie banner. Subtle motion only (emil-kowalski), reduced-motion respected. WCAG AA, visible focus, 44px tap targets.

PLAYWRIGHT MCP VERIFICATION (must run)
Flow: open app, confirm the uploader is disabled, tick (a) only and confirm it stays disabled, tick (b) and confirm it enables. Open Legal from the footer and the sidebar, switch all tabs/sections, go back and confirm the step and data are preserved. Reset session and confirm consent is cleared. Toggle Demo Mode and confirm the consent wording changes. Confirm no unresolved [PLACEHOLDER] text is visible except in the dev list. Screenshots at 390x844, 768x1024 and 1440x900 into verification/legal/. Check console errors, overflow, contrast, keyboard navigation and focus order. Fix, then re-check with targeted checks only.

DELIVERABLES
legal/*.md, legal_config.py, legal view in app.py and ui.py, styles.css additions, the HANDOFF.md legal section (5 lines), the unresolved-placeholder list, and a 5-line final report.

DISCLAIMER IN YOUR OWN OUTPUT
The drafts are templates for a hackathon prototype, not legal advice. Say that in the final report, and add to HANDOFF.md that a lawyer must review before any real-user launch.

START: invoke the skills, plan in 10 lines, then build.