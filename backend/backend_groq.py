"""Groq is the LLM. Chat memory is session-bound: the history comes from the caller's
st.session_state and is injected straight into the prompt. Nothing is written to disk."""
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from functools import cache, lru_cache
from pathlib import Path

from groq import Groq

from .safety import check_medicine

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_HISTORY = 20  # messages of earlier chat sent back each turn; older ones drop off

# The 5 prompts sit between the COPY markers in PRESCRIPTION-HELPER.txt (prompt 5 runs to end of file).
_helper = (Path(__file__).parent / "PRESCRIPTION-HELPER.txt").read_text(encoding="utf-8")
_OCR, _STRUCTURE, INFO_PROMPT, SUMMARY_PROMPT, CHAT_PROMPT = [
    re.split(r"\n\s*<{5,}", p)[0].strip()
    for p in re.split(r">{5,}\s*COPY FROM THE NEXT LINE\s*>{5,}[^\n]*\n", _helper)[1:]]

IN_LIST, GENERAL, UNCONFIRMED = "IN OUR LIST", "CONFIRMED BY PATIENT, NOT IN OUR LIST", "NOT CONFIRMED"


@cache
def _groq():
    return Groq()  # reads GROQ_API_KEY


def ask(messages: list[dict], json_mode: bool = False) -> str:
    r = _groq().chat.completions.create(
        model=MODEL, messages=messages, temperature=0.2,
        **({"response_format": {"type": "json_object"}} if json_mode else {}))
    # the model likes narrow no-break spaces and hyphens ("Pan 40"); plain ones read and match better
    return r.choices[0].message.content.translate({0x202F: " ", 0xA0: " ", 0x2011: "-"}).strip()


@lru_cache(maxsize=256)  # ponytail: general drug facts only, no patient data, so a process-wide cache is fine
def medicine_info(name: str, composition: str = "") -> dict | None:
    """Prompt 3. None when the model does not recognise the name."""
    info = json.loads(ask([{"role": "system", "content": INFO_PROMPT},
                           {"role": "user", "content": f"Medicine name: {name}\nComposition (if known): {composition or 'not known'}"}],
                          json_mode=True))
    if not isinstance(info, dict) or not info.get("recognised"):
        return None
    for k in ("precautions", "common_side_effects", "see_a_doctor_if"):  # model sometimes returns a string
        v = info.get(k) or []
        info[k] = [str(x) for x in ([v] if isinstance(v, str) else v) if str(x).strip()]
    info["used_for"] = str(info.get("used_for") or "")
    return info


def facts(rows: list[dict]) -> list[tuple[dict, str, dict | None]]:
    """(row, label, info) per confirmed line. Labels are the ones the prompts expect."""
    checks = [check_medicine(r["medicine"]) for r in rows]
    status = [c["status"] for c in checks]
    with ThreadPoolExecutor(8) as pool:
        infos = list(pool.map(lambda r, c: None if c["status"] == "unclear"
                              else medicine_info(r["medicine"].strip(), c.get("generic", "")), rows, checks))
    return [(r, IN_LIST if s == "verified" else GENERAL if i else UNCONFIRMED, i)
            for r, s, i in zip(rows, status, infos)]


def facts_text(meds) -> str:
    lines = []
    for r, label, info in meds:
        line = f"{r['medicine'] or '[unreadable name]'} - {label}"
        line += f" (contains {g})" if (g := check_medicine(r["medicine"]).get("generic")) else ""
        if info and label != UNCONFIRMED:
            line += ": " + "; ".join(f"{k.replace('_', ' ')}: {v if isinstance(v, str) else ', '.join(v)}"
                                     for k, v in info.items() if k != "recognised" and v)
        lines.append(line)
    return "\n".join(lines)


def chat_reply(history: list[dict], rows: list[dict], question: str) -> str:
    """Prompt 5 with the confirmed lines + facts in context, plus this session's earlier turns."""
    system = (CHAT_PROMPT.replace("[PRESCRIPTION DATA]", json.dumps(rows, indent=1))
              .replace("[MEDICINE FACTS]", facts_text(facts(rows))).replace("[LANGUAGE]", "English"))
    turns = [{"role": m["role"], "content": m["content"]} for m in history[-MAX_HISTORY:]]
    answer = ask([{"role": "system", "content": system}, *turns, {"role": "user", "content": question}])
    # the UI renders this as markdown: drop links/images so injected text cannot load or point to remote URLs
    return re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", answer)
