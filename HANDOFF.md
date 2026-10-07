# Scrivia frontend handoff

**Run on Windows (PowerShell or cmd)**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Keys go in `backend/env` (gitignored): `GEMINI_API_KEY=...` and `GROQ_API_KEY=...`. Optional overrides: `GEMINI_MODEL` (default `gemini-flash-latest`), `GROQ_MODEL` (default `openai/gpt-oss-120b`). Self-check: `python backend/safety.py` prints `ok`. Demo Mode preloads a sample photo; it is still read by Gemini, so it needs the internet.

**Files:** `app.py` holds the step state machine and layout. `ui.py` has the HTML helpers (escaped, via `st.html`). `styles.css` holds the tokens and all styling; it is injected once and its fonts are inlined. `backend/` is the real backend: `backend_ocr.py` (Gemini reads the photo with the rules in `PRESCRIPTION-OCR.txt`), `backend_groq.py` (Groq LLM, prompts 3-5 parsed from `PRESCRIPTION-HELPER.txt`, chat), `report_generator.py` (report), `safety.py` (verified name list + frequency in words), `report.py` (optional PDF, not wired into the UI), `chatbot.py` (terminal chat: `python -m backend.chatbot photo.jpg`). `dummy_data.py` has the 3 demo samples. `.streamlit/config.toml` sets the theme. `assets/` holds the fonts, placeholder images and sample slips. `IMAGE_PROMPTS.md` lists the images to generate. `verification/` holds the Playwright screenshots.

**Contract.** `app.py` imports only these four functions:
- `extract_prescription(image_bytes: bytes, filename: str) -> list[dict]`, where each dict has the keys `medicine`, `dosage` and `frequency`
- `check_medicine(name: str) -> dict`, returning `{status: verified|suggest|unrecognized|unclear, suggestion: str|None}`
- `generate_report(rows: list[dict]) -> str`, returning markdown. Use one `## Name` section per medicine with lines in the form `**Label:** text`. `Dose` and `When` go in the card header, and a `Note` label renders as a warning. Without `##` sections, the report falls back to plain `st.markdown`.
- `chat_reply(history: list[dict], rows: list[dict], question: str) -> str`, returning markdown

**Backend:** `app.py` does `from backend import ...`. Backend functions raise on failure; the UI catches them, shows an error state and prints the reason to the terminal. **Chat memory is session-bound:** `chat_history` lives in `st.session_state` only, and the confirmed lines, medicine facts and last 20 messages are injected straight into the Groq prompt each turn. Nothing is written to disk. `check_medicine` is cached per name. Any field containing `UNCLEAR` marks its line as unclear.

**Session state:** `step` (1/2/3), `demo_mode`, `selected_sample`, `raw_rows` (as read, with `_id`), `verified_df` (the current table, with a hidden `_id` column), `chat_history`. Helper keys: `image_bytes`, `acked` (ids of lines the user kept), `editor_ver` (the editor key is `rx_editor_{n}` and changes only when code edits the table), `report`, `error`.

**Gate:** Confirm stays disabled while any line is unclear, or is flagged and unchanged without being acknowledged. The hint names the blocking line numbers.

**Fragile CSS selectors (Streamlit 1.65.0, pinned):** `stMainBlockContainer`, `stHeader`, `stSidebar`, `stBaseButton-*`, `stFileUploaderDropzone`, `stDataFrame` (canvas grid: only the frame can be styled), `stChatMessage`, `stChatMessageAvatar*`, `stChatInput*`, `stImage`, `stCheckbox label`, `[data-baseweb="select"]`, the `.st-key-*` container classes (`review`, `flag_actions_*`, `chips`, `ask`, `step2_actions`, `step3_actions`) and `:has(.st-key-review)` for the mobile reorder. Re-check these whenever you upgrade Streamlit.

**Known limits:**
- `st.html` strips `<style>` and SVG in 1.65, so the stylesheet goes in through one `st.markdown(unsafe_allow_html=True)` call and the icons are CSS masks.
- Streamlit's tooltip icons and the selectbox chevron are under 44px.
- On OneDrive, the file watcher sometimes misses Python edits. Restart `streamlit run` after editing a module.
