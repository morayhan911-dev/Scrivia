/ponytail
/caveman
name : NexCura (the prompt says propose ideas for the name i dont want it now go with the name nexcura )
TOKEN RULES (apply to this and every chat)
- Use /ponytail and /caveman at the start of every chat. If either is not installed, say so in one line and continue terse.
- Tokens are scarce. Plan in 10 lines max. No long explanations. Do not re-read files you just wrote. Use targeted edits, never paste whole files back. Report each milestone in 8 lines max. Ask me questions only when blocked, and batch them.
- Work in milestones (below). Commit after each. Stop after M0 for my approval.

MANDATORY TOOLS (must use, none optional)
Skills: impeccable, gpt-taste, emil-kowalski, ui-ux-pro-max, frontend-design. Read each before designing anything. Take inspiration from all of them and combine them. If a skill is missing, tell me immediately. Do not silently substitute.
MCP: Playwright MCP, used for verification (details in M6). If it is not connected, tell me and stop.

ROLE AND SCOPE
You are building the FRONTEND ONLY of a hackathon app. A teammate is building the Python backend (Gemini OCR + Groq/Llama). You use dummy data behind a stub file. Do NOT call any real API. Do NOT add API keys, Gemini, Groq or ML code. Do NOT edit any backend file my teammate creates.

PRODUCT
A prescription explainer in three steps: 1) upload a prescription image, 2) human verifies the extracted medicines, 3) plain-English report plus chat about the verified prescription.
Core idea: the AI does not get trusted blindly. The human verification gate is the product's differentiator, so Step 2 must be the visual centerpiece of the whole app.

TECH SPLIT (important)
- Streamlit does ALL functionality: st.file_uploader, st.button, st.data_editor, st.chat_input, st.chat_message, st.session_state, st.sidebar, st.columns.
- HTML/CSS does ALL design and showcase: hero, step indicator, cards, badges, status chips, typography, spacing, empty states, report layout, footer, disclaimers.
- Load ONE styles.css, injected once at the top of app.py via st.html (verify with Playwright that <style> survives; only if st.html strips it, fall back to st.markdown(unsafe_allow_html=True) for that single injection). HTML snippets are built by small render helpers in ui.py. No other unsafe HTML.
- Also set base theme in .streamlit/config.toml.
- Styling Streamlit's own widgets (uploader, data_editor, chat) means targeting its internal selectors. Keep these minimal and commented, and pin the Streamlit version in requirements.txt.
- Python deps for the frontend: streamlit, pandas, pillow only.
- I am on Windows. Give PowerShell/cmd commands (python -m venv venv, venv\Scripts\activate, streamlit run app.py).

FILES TO CREATE
app.py (step state machine + layout), ui.py (HTML render helpers), styles.css, backend_stub.py, dummy_data.py, .streamlit/config.toml, requirements.txt, assets/ (placeholders), IMAGE_PROMPTS.md, HANDOFF.md (max 40 lines), verification/ (screenshots).

STATE (st.session_state keys)
step (1/2/3), demo_mode, selected_sample, raw_rows, verified_df, chat_history. Use a static key on st.data_editor. Never keep data in plain variables across reruns. Do not trigger extraction twice on rerun.

BACKEND CONTRACT (stub now, teammate swaps later)
backend_stub.py exposes exactly these functions. app.py imports only these, so swapping to the real backend is a one-line import change:
- extract_prescription(image_bytes: bytes, filename: str) -> list[dict]  # keys: medicine, dosage, frequency
- check_medicine(name: str) -> dict  # {status: 'verified'|'suggest'|'unrecognized'|'unclear', suggestion: str|None}
- generate_report(rows: list[dict]) -> str  # markdown
- chat_reply(history: list[dict], rows: list[dict], question: str) -> str
Stub returns canned data from dummy_data.py. chat_reply uses simple keyword matching with 5-6 canned answers plus a safe fallback ("I can only explain what is in your verified prescription...").

DUMMY DATA
3 sample prescriptions in dummy_data.py, each with realistic Indian medicines, dosage and frequency:
 1) clean, all verified;
 2) a look-alike drug trap (for example an OCR misread like "Folite" flagged as "Did you mean Folvite?") plus one "UNCLEAR - PLEASE VERIFY" field;
 3) a mix of verified and unrecognized rows.
Each has a matching report and canned chat answers. Sidebar Demo Mode toggle plus a sample selector drive these. Map an uploaded filename to a sample, and fall back to the selected sample.

SCREENS
Persistent: sidebar (app name, Demo Mode toggle, sample selector, collapsed "Connections" placeholder for the teammate's keys, a non-dismissible disclaimer: educational literacy tool, not diagnosis, consult a doctor, plus a short privacy note: processed in memory, not stored). A 3-step progress indicator sits at the top.
Step 1: landing hero plus upload area, image preview, extract button, loading state, error state.
Step 2 (centerpiece): editable table. Every row shows a status chip (verified / did you mean X / unrecognized / unclear). Statuses must never rely on colour alone: use icon plus text. Flagged rows are visually prominent. "Confirm" is disabled until every flagged row is edited or explicitly acknowledged, and it says why when disabled. Also: restart button, a way to add a missing row, and a clear "AI read this, you confirm it" framing.
Step 3: report in a clean readable layout (one card per medicine, not a wall of text), the chat below it with suggested question chips, a reset button, and the disclaimer repeated at the bottom of the report.
Also design: empty, loading, error and disabled states for everything.

DESIGN DIRECTION
- You choose the palette, type pairing and tokens by applying the skills above. Define them as CSS variables. Light mode primary. Calm, clinical, modern, trustworthy, generous whitespace, strong hierarchy.
- ABSOLUTELY NO AI SLOP: no purple/blue "AI" gradients, no gradient blobs, no glassmorphism, no glows, no floating particles, no emoji as icons, no generic "AI-powered / intelligent / magic" copy, no card-everything layout, no default-Streamlit look. Write specific, human microcopy.
- Fonts must work offline (demo-day Wi-Fi may die): bundle font files in assets/fonts or use a strong system stack. No runtime CDN dependency.
- WCAG AA contrast, visible focus states, tap targets of at least 44px.
- Equally polished on desktop and mobile (test 390, 768, 1440). Columns must stack cleanly. No horizontal scroll.
- Motion (emil-kowalski): subtle and purposeful. Under 300ms, custom ease-out curves, transform and opacity only, only on state transitions (step change, chip state, message arrival). Nothing on repeated actions. Respect prefers-reduced-motion.

IMAGES: I GENERATE THEM, YOU DO NOT
Do NOT generate images. After the palette is locked, write IMAGE_PROMPTS.md with copy-paste GPT-image prompts for:
- logo/wordmark
- hero illustration
- upload empty-state art
- the 3 synthetic sample prescriptions (fictional doctor and clinic, no real person data, handwriting style; the prompt must dictate the EXACT medicine lines matching dummy_data.py)
- ANY other asset you decide the design needs (favicon, report header art, empty/error art, chat avatar, etc.). Tell me explicitly what extra I must generate.
For each: filename, drop path in assets/, size, aspect ratio, format/transparency, style tied to the chosen palette hex values, and a negative prompt. Keep text inside generated images minimal (image models mangle text). Build a CSS/typographic wordmark as a fallback. Use neutral placeholders at the exact aspect ratios until my images arrive. If my generated prescription text differs from dummy_data.py, I will tell you and you adjust dummy_data.py.

PRODUCT NAME
At M0, use web search to research and propose 5 minimalist, modern, sleek names not obviously taken. Check company, trademark, domain and app-store conflicts, then give a short table with conflict notes, plus your recommendation (say "no obvious conflicts found", not "cleared"). Use a single APP_NAME constant until I choose.

MILESTONES
M0: read skills, research names, lock palette/type/tokens, write IMAGE_PROMPTS.md. Report in 10 lines. STOP for my approval.
M1: project setup, 3-step skeleton working end to end with the stub and dummy data, unstyled.
M2: styles.css, hero, step indicator, sidebar, disclaimer.
M3: Step 2 verification polish (centerpiece).
M4: report cards plus chat plus suggestion chips.
M5: responsive pass plus motion pass plus all empty/loading/error states.
M6: Playwright verification (below), fix, then write HANDOFF.md.

PLAYWRIGHT MCP VERIFICATION (must run)
Start streamlit in the background. Full click-through with Demo Mode on, for all 3 samples: upload, extract, fix the flagged row, confirm (also check that the disabled state blocks early confirm), report, ask 2 chat questions, reset.
Take screenshots of each step at 390x844, 768x1024 and 1440x900 into verification/. Check console errors, horizontal overflow, contrast, focus visibility, tap-target size, and reduced-motion behaviour. Fix, then re-check. Between milestones use targeted checks only. Run the full flow once at M6 and once more after the final fix.

HANDOFF.md (max 40 lines)
Run commands for Windows, the file map, the 4-function contract, session-state keys, how to swap backend_stub for the real backend, and known fragile CSS selectors.

DEFINITION OF DONE
Full flow works in Demo Mode with zero network. Contract documented. Design reads as hand-made, not templated. Playwright passes at all 3 widths. IMAGE_PROMPTS.md is complete. No real API code anywhere.

START NOW: invoke the skills, then do M0 only.