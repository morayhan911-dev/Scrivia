"""Plain-English report for the confirmed lines, written by Groq (prompts 3 and 4)."""
import json

from .backend_groq import GENERAL, IN_LIST, SUMMARY_PROMPT, ask, facts, facts_text
from .safety import explain_frequency

NOTES = {GENERAL: "General information, not checked against our list. Please confirm with your pharmacist.",
         "NOT CONFIRMED": "We could not confirm this medicine, so no details are given. Please ask your pharmacist."}
SECTIONS = (("precautions", "Precautions"), ("common_side_effects", "Common side effects"),
            ("see_a_doctor_if", "See a doctor if"))


def generate_report(rows: list[dict]) -> str:
    """Markdown: summary paragraph, then one '## Name' section of '**Label:** text' lines per medicine."""
    meds = facts(rows)
    summary = ask([{"role": "system", "content": SUMMARY_PROMPT},
                   {"role": "user", "content": f"PRESCRIPTION DATA:\n{json.dumps(rows, indent=1)}\n\n"
                                               f"MEDICINE FACTS:\n{facts_text(meds)}"}])
    out = ["\n".join(line.strip() for line in summary.splitlines() if line.strip())]  # one line per medicine
    for r, label, info in meds:
        out += ["", f"## {r['medicine'] or 'Unreadable name'}", f"**Dose:** {r['dosage']}",
                f"**When:** {explain_frequency(r['frequency'])}"]
        if info and info.get("used_for"):
            out.append(f"**What it is for:** {info['used_for']}")
        out += [f"**{title}:** " + "; ".join(info[k]) for k, title in SECTIONS if info and info.get(k)]
        if label != IN_LIST:
            out.append(f"**Note:** {NOTES[label]}")
    return "\n".join(out)
