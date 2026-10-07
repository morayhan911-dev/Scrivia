"""Scrivia: upload a prescription, check what was read, then understand it. Frontend only."""
import io

import pandas as pd
import streamlit as st
from PIL import Image

import ui
# Backend contract. To use the real backend, change only this import.
from backend_stub import chat_reply, check_medicine, extract_prescription, generate_report
from dummy_data import SAMPLES, sample_for

APP_NAME = "Scrivia"
COLS = ["medicine", "dosage", "frequency"]
SUGGESTIONS = ["When do I take each one?", "Should I take these with food?",
               "What side effects should I watch for?", "What if I miss a dose?"]

st.set_page_config(page_title=f"{APP_NAME}: understand your prescription", page_icon="assets/favicon.png",
                   layout="wide", initial_sidebar_state="auto")
# The one stylesheet injection. st.html strips <style> in 1.65 (checked with Playwright), so this
# single call uses st.markdown. No other unsafe HTML anywhere.
st.markdown(ui.css(), unsafe_allow_html=True)

DEFAULTS = {"step": 1, "demo_mode": True, "selected_sample": "fever", "raw_rows": list, "verified_df": None,
            "chat_history": list, "image_bytes": None, "acked": list, "editor_ver": 0, "report": "", "error": ""}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v() if callable(v) else v
ss = st.session_state

check = st.cache_data(check_medicine, show_spinner=False)  # real backend may be slow: check each name once


def row_status(row):
    if not str(row["medicine"]).strip() or any("UNCLEAR" in str(row[c]).upper() for c in COLS):
        return {"status": "unclear", "suggestion": None}
    return check(str(row["medicine"]))


def blocking(df):
    """Line numbers (1-based) that still need a human decision."""
    raw = {r["_id"]: r for r in ss.raw_rows}
    out = []
    for n, row in enumerate(df.to_dict("records"), 1):
        s = row_status(row)["status"]
        if s == "verified" or row["_id"] in ss.acked:
            continue
        unchanged = row["_id"] in raw and all(row[c] == raw[row["_id"]][c] for c in COLS)
        if s == "unclear" or unchanged:
            out.append(n)
    return out


def reset():
    for k in ("raw_rows", "verified_df", "chat_history", "image_bytes", "acked", "report", "error"):
        del ss[k]
    ss.step = 1
    ss.editor_ver += 1


def set_df(df):
    ss.verified_df = df.reset_index(drop=True)
    ss.editor_ver += 1  # new editor key: the table re-renders from the updated frame


def apply_fix(i, value):
    df = ss.verified_df.copy()
    df.at[i, "medicine"] = value
    set_df(df)


def remove_row(i):
    set_df(ss.verified_df.drop(index=i))


def toggle_ack(rid):
    ss.acked = [a for a in ss.acked if a != rid] if rid in ss.acked else [*ss.acked, rid]


def add_row():
    df = ss.verified_df
    set_df(pd.concat([df, pd.DataFrame([{"_id": int(df["_id"].max()) + 1 if len(df) else 0, **dict.fromkeys(COLS, "")}])]))


def go(step):
    ss.step = step


# ---------- sidebar ----------
with st.sidebar:
    st.html(ui.wordmark(APP_NAME))
    st.toggle("Demo mode", key="demo_mode", help="Uses built-in sample prescriptions. Works with no internet.")
    st.selectbox("Sample prescription", list(SAMPLES), key="selected_sample",
                 format_func=lambda k: SAMPLES[k]["label"], disabled=not ss.demo_mode)
    with st.expander("Connections"):
        st.caption("The backend keys go here once it is connected. Demo mode needs none.")
        st.text_input("Text reading service", type="password", disabled=True, placeholder="Not connected")
        st.text_input("Explanation service", type="password", disabled=True, placeholder="Not connected")
    st.html(ui.disclaimer())

st.html(ui.steps(ss.step))

# ---------- step 1: upload ----------
if ss.step == 1:
    st.html(ui.hero(APP_NAME))
    sample = SAMPLES[ss.selected_sample]
    with st.container(key="upload"):
        left, right = st.columns([3, 2], gap="large")
        with left:
            up = st.file_uploader("Photo of your prescription", type=["jpg", "jpeg", "png", "webp"],
                                  help="JPG, PNG or WEBP. One page at a time.")
            if up:
                data, fname = up.getvalue(), up.name
                if ss.demo_mode and not sample_for(fname):
                    fname = sample["filename"]  # demo: unknown uploads fall back to the selected sample
            elif ss.demo_mode:
                data, fname = (ui.ROOT / "assets/samples" / sample["filename"]).read_bytes(), sample["filename"]
                st.html(ui.sample_note(sample["label"]))
            else:
                data = fname = None
            if ss.error:
                st.html(ui.error(ss.error))
            clicked = st.button("Read this prescription", type="primary", disabled=data is None,
                                icon=":material/document_scanner:")
            if data is None:
                st.caption("Add a photo first, or turn on demo mode in the sidebar.")
        with right:
            if data:
                st.image(data, caption=up.name if up else "Sample photo", width="stretch")
            else:
                st.html(ui.upload_empty())
    if clicked:
        ss.error = ""
        try:
            Image.open(io.BytesIO(data)).verify()
        except Exception:
            ss.error = "That file is not an image we can open. Try a JPG or PNG photo of the slip."
            st.rerun()
        with st.spinner("Reading each line of your prescription..."):
            try:
                rows = extract_prescription(data, fname)
            except Exception:
                rows, ss.error = None, "The reading service did not answer. Check your connection and try again."
        if rows == []:
            ss.error = "No medicine lines were found. Retake the photo flat, in good light, with every line in frame."
        if rows:
            ss.raw_rows = [{"_id": i, **{c: str(r.get(c, "")) for c in COLS}} for i, r in enumerate(rows)]
            ss.verified_df = pd.DataFrame(ss.raw_rows)
            ss.image_bytes, ss.acked, ss.step = data, [], 2
            ss.editor_ver += 1
        st.rerun()

# ---------- step 2: verify (centerpiece) ----------
elif ss.step == 2:
    df = ss.verified_df
    records = df.to_dict("records")
    stats = [row_status(r) for r in records]
    raw_flagged = {r["_id"] for r in ss.raw_rows if row_status(r)["status"] != "verified"}
    # a line stays in the review list if the scan flagged it or it is flagged now (fixed lines show as done)
    flagged = [(n, r, s) for n, (r, s) in enumerate(zip(records, stats), 1)
               if s["status"] != "verified" or r["_id"] in raw_flagged]
    pending = blocking(df)
    st.html(ui.step_head(2, "Check what we read",
                         "Handwriting gets misread. Nothing moves forward until you have looked at every flagged line."))
    st.html(ui.framing(len(df), len(flagged), len(flagged) - len(pending)))

    photo, review = st.columns([2, 3], gap="large")
    with photo:
        st.image(ss.image_bytes, caption="Your photo", width="stretch")
    with review, st.container(key="review"):
        if not flagged:
            st.html(ui.all_clear())
        for n, row, s in flagged:
            acked = row["_id"] in ss.acked
            fixed = s["status"] == "verified"
            st.html(ui.flag_item(n, row, s["status"], s["suggestion"], n not in pending, fixed))
            if fixed:
                continue
            with st.container(horizontal=True, key=f"flag_actions_{row['_id']}"):
                if s["suggestion"] and not acked:
                    st.button(f"Use {s['suggestion']}", key=f"fix_{row['_id']}", type="primary",
                              on_click=apply_fix, args=(n - 1, s["suggestion"]))
                if not row["medicine"].strip():
                    st.button("Remove this line", key=f"rm_{row['_id']}", on_click=remove_row, args=(n - 1,))
                else:
                    st.button("Undo" if acked else "Keep as written", key=f"ack_{row['_id']}",
                              on_click=toggle_ack, args=(row["_id"],))

    st.subheader("All lines", anchor=False)
    st.caption("Click any cell to correct it. Select a row's left edge and press Delete to remove a line.")
    view = df.copy()
    view.insert(0, "status", [ui.grid_status(s["status"], s["suggestion"]) for s in stats])
    out = st.data_editor(
        view, key=f"rx_editor_{ss.editor_ver}", hide_index=True, num_rows="dynamic", width="stretch",
        column_order=["status", *COLS], disabled=["status"],
        column_config={"status": st.column_config.TextColumn("Status", width="medium"),
                       "medicine": st.column_config.TextColumn("Medicine", required=True),
                       "dosage": st.column_config.TextColumn("Dose"),
                       "frequency": st.column_config.TextColumn("How often")})
    out = out.drop(columns="status").reset_index(drop=True)
    out[COLS] = out[COLS].fillna("").astype(str)
    new = out["_id"].isna()
    if new.any():
        start = int(pd.concat([df["_id"], out["_id"]]).max()) + 1
        out.loc[new, "_id"] = range(start, start + int(new.sum()))
    out["_id"] = out["_id"].astype(int)
    if not out.astype(str).equals(df.astype(str)):
        set_df(out)
        st.rerun()
    st.button("Add a missing line", icon=":material/add:", on_click=add_row)

    st.html(ui.confirm_hint(pending))
    with st.container(horizontal=True, key="step2_actions"):
        st.button("Start over", on_click=reset, icon=":material/restart_alt:")
        confirm = st.button(f"Confirm {len(df)} line{'s' if len(df) != 1 else ''}", type="primary",
                            disabled=bool(pending) or df.empty, icon=":material/check:")
    if ss.error:
        st.html(ui.error(ss.error))
    if confirm:
        ss.error = ""
        with st.spinner("Writing your plain-English report..."):
            try:
                ss.report = generate_report(df[COLS].to_dict("records"))
                ss.chat_history, ss.step = [], 3
            except Exception:
                ss.error = "The report could not be written. Try again in a moment."
        st.rerun()

# ---------- step 3: report + chat ----------
else:
    rows = ss.verified_df[COLS].to_dict("records")
    st.html(ui.step_head(3, "Your prescription, in plain English",
                         "Built only from the lines you confirmed. Keep your doctor's instructions first."))
    html = ui.report(ss.report)
    if html:
        st.html(html)
    else:
        st.markdown(ss.report)
    st.html(ui.disclaimer())

    st.subheader("Ask about these medicines", anchor=False)
    history = st.container(key="chat")
    with st.container(horizontal=True, key="chips"):
        chip_q = next((q for q in SUGGESTIONS if st.button(q, key=f"chip_{q}")), None)
    with st.container(key="ask"):  # inside a container = inline under the report, not pinned to the viewport
        q = st.chat_input("Ask about a medicine on this prescription") or chip_q
    with history:
        if not ss.chat_history and not q:
            st.html(ui.chat_empty(len(rows)))
        for m in ss.chat_history:
            with st.chat_message(m["role"], avatar=":material/person:" if m["role"] == "user" else ":material/description:"):
                st.markdown(m["content"])
        if q:
            with st.chat_message("user", avatar=":material/person:"):
                st.markdown(q)
            with st.chat_message("assistant", avatar=":material/description:"), st.spinner("Checking your lines..."):
                try:
                    a = chat_reply(ss.chat_history, rows, q)
                except Exception:
                    a = "Sorry, I could not answer that just now. Please try again."
                st.markdown(a)
            ss.chat_history += [{"role": "user", "content": q}, {"role": "assistant", "content": a}]

    with st.container(horizontal=True, key="step3_actions"):
        st.button("Back to checking", on_click=go, args=(2,), icon=":material/arrow_back:")
        st.button("Start a new prescription", on_click=reset, type="primary", icon=":material/restart_alt:")

st.html(ui.footer())
