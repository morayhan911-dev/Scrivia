"""Plain-English report for the confirmed lines, written by Groq (prompts 3 and 4)."""
import json

from . import report
from .backend_groq import IN_LIST, SUMMARY_PROMPT, ask, facts, facts_text
from .safety import check_medicine, explain_frequency

NOT_FOUND = "We could not find this medicine, so no details are given. Please ask your pharmacist."
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
        if info and check_medicine(r["medicine"])["status"] != "verified":
            out.append("**Name check:** Confirmed by you")
        if label != IN_LIST:
            out.append(f"**Note:** {NOT_FOUND}")
    return "\n".join(out)


def report_pdf(rows: list[dict], report_md: str) -> bytes:
    """The same report as a PDF. Reuses the cached medicine facts, so no new LLM calls."""
    meds = facts(rows)
    data = {"medicines": [{"name": r["medicine"], "strength": r["dosage"], "frequency": r["frequency"]} for r in rows]}
    infos = [{**(info or {}), "source": "list" if label == IN_LIST else "unconfirmed", "recognised": info is not None}
             for _, label, info in meds]
    summary = report_md.split("\n## ")[0]
    return report.make_pdf(data, [check_medicine(r["medicine"]) for r in rows], summary, infos)
