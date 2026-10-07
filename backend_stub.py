"""Stub backend with canned data. The real backend must expose these same 4 functions.
To swap: change the one import line in app.py. No network, no keys."""
import re
import time

from dummy_data import FALLBACK, KNOWN, LOOKALIKES, MED_INFO, SAMPLES, sample_for


def extract_prescription(image_bytes: bytes, filename: str) -> list[dict]:
    time.sleep(1.2)  # ponytail: fake latency so the loading state is visible
    key = sample_for(filename) or "fever"
    return [dict(r) for r in SAMPLES[key]["rows"]]


def check_medicine(name: str) -> dict:
    n = name.strip().lower()
    if not n or "unclear" in n:
        return {"status": "unclear", "suggestion": None}
    if n in KNOWN:
        return {"status": "verified", "suggestion": None}
    if n in LOOKALIKES:
        return {"status": "suggest", "suggestion": LOOKALIKES[n]}
    return {"status": "unrecognized", "suggestion": None}


def plain_schedule(freq: str) -> str:
    """'1-0-1 after food, 30 days' -> 'Morning and night, after food, for 30 days'."""
    if "UNCLEAR" in freq.upper():
        return "Not readable on the slip. Ask your doctor or pharmacist before taking this."
    m = re.match(r"\s*(\d)\s*-\s*(\d)\s*-\s*(\d)\s*(.*)", freq)
    if not m:
        return freq
    slots = [s for s, c in zip(("morning", "afternoon", "night"), m.groups()[:3]) if c != "0"]
    when = ", ".join(slots[:-1]) + " and " + slots[-1] if len(slots) > 1 else (slots or ["as directed"])[0]
    rest = re.sub(r"(\d+) days", r"for \1 days", m[4].strip())
    return f"{when.capitalize()}, {rest}" if rest else when.capitalize()


def generate_report(rows: list[dict]) -> str:
    time.sleep(0.6)
    n = len(rows)
    out = [f"You confirmed {n} medicine{'s' if n != 1 else ''}. Here is what each one is for and how to take it."]
    for r in rows:
        info = MED_INFO.get(r["medicine"].strip().lower())
        out += ["", f"## {r['medicine']}", f"**Dose:** {r['dosage']}", f"**When:** {plain_schedule(r['frequency'])}"]
        if info:
            out += [f"**What it is for:** {info[0]}", f"**How to take it:** {info[1]}",
                    f"**Tell your doctor if you notice:** {info[2]}"]
        else:
            out.append("**Note:** We have no notes for this name. Show this line to your pharmacist before taking it.")
    return "\n".join(out)


def chat_reply(history: list[dict], rows: list[dict], question: str) -> str:
    time.sleep(0.4)
    q = question.lower()
    known = [(r, MED_INFO.get(r["medicine"].strip().lower())) for r in rows]
    for r, info in known:
        if info and r["medicine"].lower().split()[0] in q:
            return f"**{r['medicine']}**: {info[0]} {info[1]} Watch for: {info[2]}"

    def each(fn):
        return "\n".join(f"- **{r['medicine']}**: {fn(r, i)}" for r, i in known)

    if any(w in q for w in ("side effect", "watch", "reaction")):
        return "Things to watch for:\n" + each(lambda r, i: i[2] if i else "No notes. Ask your pharmacist.")
    if any(w in q for w in ("food", "eat", "empty stomach", "meal")):
        return "How to take each one:\n" + each(lambda r, i: i[1] if i else r["frequency"])
    if any(w in q for w in ("when", "time", "schedule", "morning", "night", "how long", "days")):
        return "Your daily schedule:\n" + each(lambda r, i: plain_schedule(r["frequency"]))
    if any(w in q for w in ("miss", "forgot", "skip")):
        return ("If you miss a dose, take it when you remember, unless it is almost time for the next one. "
                "Then skip the missed dose. Never take two doses at once to catch up.")
    if any(w in q for w in ("alcohol", "drink", "beer", "wine")):
        return ("Best avoided while on these medicines. Alcohol adds to drowsiness and strains the liver "
                "and stomach. Ask your doctor what is safe for you.")
    return FALLBACK
