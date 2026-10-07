"""Groq is the LLM. Chat memory is session-bound: the history comes from the caller's
st.session_state and is injected straight into the prompt. Nothing is written to disk."""
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from functools import cache
from pathlib import Path

from groq import Groq

from .safety import check_medicine, lookup_composition

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_HISTORY = 20  # messages of earlier chat sent back each turn; older ones drop off

# The 5 prompts sit between the COPY markers in PRESCRIPTION-HELPER.txt (prompt 5 runs to end of file).
_helper = (Path(__file__).parent / "PRESCRIPTION-HELPER.txt").read_text(encoding="utf-8")
_OCR, _STRUCTURE, INFO_PROMPT, SUMMARY_PROMPT, CHAT_PROMPT = [
    re.split(r"\n\s*<{5,}", p)[0].strip()
    for p in re.split(r">{5,}\s*COPY FROM THE NEXT LINE\s*>{5,}[^\n]*\n", _helper)[1:]]

# The name lists (brands + 150 generics) only spell-check and spare the patient a confirmation click.
# Facts always come from Groq: a name is IN OUR LIST once Groq has facts for it, however it was confirmed.
IN_LIST, UNCONFIRMED = "IN OUR LIST", "NOT CONFIRMED"


@cache
def _groq():
    return Groq(max_retries=5)  # reads GROQ_API_KEY; retries wait out the free tier's 8k tokens/minute limit


def ask(messages: list[dict], json_mode: bool = False) -> str:
    r = _groq().chat.completions.create(
        model=MODEL, messages=messages, temperature=0.2,
        # low effort: ~10x faster and steadier on gpt-oss (medium sometimes called Pan 40 "not recognised")
        **({"reasoning_effort": "low"} if MODEL.startswith("openai/gpt-oss") else {}),
        **({"response_format": {"type": "json_object"}} if json_mode else {}))
    # the model likes narrow no-break spaces and hyphens ("Pan 40"); plain ones read and match better
    return r.choices[0].message.content.translate({0x202F: " ", 0xA0: " ", 0x2011: "-"}).strip()


# ponytail: general drug facts only, no patient data, so a process-wide cache is fine.
# Only recognised answers are cached, so one flaky "not recognised" never sticks for the whole server.
_INFO: dict[tuple[str, str], dict] = {}


def medicine_info(name: str, composition: str = "") -> dict | None:
    """Prompt 3. None when the model does not recognise the name (brand, then the known generic)."""
    key = (name, composition)
    if key not in _INFO:
        info = _ask_info(name, composition) or (_ask_info(f"{composition}, as {name}", composition) if composition else None)
        if info is None:
            return None
        _INFO[key] = info
    return _INFO[key]


def _ask_info(name: str, composition: str) -> dict | None:
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
    """(row, label, info) per confirmed line. Labels are the ones the prompts expect.
    Groq only writes facts once we know what a medicine contains (name lists or the medicine database):
    from a brand name alone it invents ingredients or describes the wrong drug."""
    looked_up = []  # (name as Groq sees it, composition)
    for r in rows:
        c, name = check_medicine(r["medicine"]), r["medicine"].strip()
        comp, products = ("", "") if c["status"] == "unclear" else (c.get("generic", ""), "")
        if c["status"] != "unclear" and not comp:
            comp, products = lookup_composition(name)
        looked_up.append((f"{name} (sold as {products})" if products else name, comp))

    def info(name, comp):
        found = medicine_info(name, comp) if comp else None
        return {**found, "composition": comp} if found else None

    with ThreadPoolExecutor(8) as pool:
        infos = list(pool.map(info, *zip(*looked_up))) if rows else []
    return [(r, IN_LIST if i else UNCONFIRMED, i) for r, i in zip(rows, infos)]


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
