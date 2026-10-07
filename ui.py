"""HTML render helpers. Every snippet goes through st.html; all user/backend text is escaped."""
import base64
import re
from html import escape
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent

# Lucide-style 24px stroke icons, decorative (text label always sits next to them).
_PATHS = {
    "verified": '<path d="M20 6 9 17l-5-5"/>',
    "suggest": '<path d="m16 3 4 4-4 4"/><path d="M20 7H4"/><path d="m8 21-4-4 4-4"/><path d="M4 17h16"/>',
    "unclear": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "unrecognized": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "checked": '<path d="M20 6 9 17l-5-5"/>',
    "error": '<circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
}
LABELS = {
    "verified": "Verified",
    "suggest": "Did you mean {s}?",
    "unclear": "Unclear, please check",
    "unrecognized": "Not recognised",
    "checked": "Checked by you",
}
GRID = {"verified": "✓ Verified", "suggest": "⇄ Did you mean {s}?", "unclear": "? Unclear, please check",
        "unrecognized": "✕ Not recognised"}  # plain glyphs (not emoji) for the canvas table


def icon(name):
    return (f'<svg class="ic" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_PATHS[name]}</svg>')


@st.cache_data
def css():
    """styles.css with bundled fonts inlined as data URIs, so nothing loads from the network."""
    text = (ROOT / "styles.css").read_text(encoding="utf-8")
    return "<style>" + re.sub(r'url\("(assets/fonts/[^"]+)"\)', lambda m: f'url("{data_uri(m[1])}")', text) + "</style>"


@st.cache_data
def data_uri(rel):
    p = ROOT / rel
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".woff2": "font/woff2"}[p.suffix]
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def wordmark(name):
    return f'<div class="wordmark" aria-label="{escape(name)}"><span>{escape(name)}</span></div>'


def steps(current):
    names = ["Upload", "Check", "Understand"]
    items = "".join(
        f'<li class="steps__item" data-state="{"done" if i < current else "now" if i == current else "next"}"'
        f'{" aria-current=step" if i == current else ""}><span class="steps__n">{i}</span>{n}</li>'
        for i, n in enumerate(names, 1))
    return f'<nav aria-label="Progress"><ol class="steps">{items}</ol></nav>'


def hero(name):
    return f"""<section class="hero" data-step="1">
  <div class="hero__copy">
    <h1>Know what your prescription says before you take it.</h1>
    <p class="lede">Photograph the slip. {escape(name)} reads each line, you check every line it read,
    and only then do you get a plain explanation of each medicine.</p>
  </div>
  <img class="hero__art" src="{data_uri('assets/hero.png')}" alt="" width="1600" height="1200">
</section>"""


def upload_empty():
    return f"""<div class="empty"><img src="{data_uri('assets/upload-empty.png')}" alt="" width="800" height="600">
  <p><strong>No photo yet.</strong> Lay the slip flat in good light and get every line in frame.</p></div>"""


def sample_note(label):
    return f'<p class="note">Demo mode is using <strong>{escape(label)}</strong>. Upload a photo to replace it.</p>'


def error(msg):
    return f"""<div class="callout callout--error" role="alert">
  <img src="{data_uri('assets/error.png')}" alt="" width="600" height="450">
  <div><p class="callout__title">{icon('error')} We could not read that.</p><p>{escape(msg)}</p></div></div>"""


def step_head(step, title, lede):
    return f'<header class="step-head" data-step="{step}"><h2>{escape(title)}</h2><p class="lede">{lede}</p></header>'


def framing(total, flagged):
    need = f"<strong>{flagged} need your eyes.</strong>" if flagged else "<strong>All of them match known medicines.</strong>"
    return f"""<div class="framing">
  <div class="framing__part"><span class="framing__k">Read by the scanner</span><span class="framing__v">{total} lines</span></div>
  <span class="framing__arrow" aria-hidden="true"></span>
  <div class="framing__part framing__part--you"><span class="framing__k">Confirmed by you</span><span class="framing__v">{need}</span></div>
</div>"""


def chip(status, suggestion=None):
    label = LABELS[status].format(s=escape(suggestion or ""))
    return f'<span class="chip chip--{status}">{icon(status)}<span>{label}</span></span>'


def grid_status(status, suggestion=None):
    return GRID[status].format(s=suggestion or "")


def flag_item(line_no, row, status, suggestion, resolved):
    state = "checked" if resolved else status
    hint = {
        "suggest": f"The scan read <b>{escape(row['medicine'])}</b>. A known medicine is spelled <b>{escape(suggestion or '')}</b>. Compare with your photo.",
        "unclear": "Part of this line could not be read. Type what the slip says, or keep it and ask your doctor.",
        "unrecognized": "This name is not in our list. It may be a misread or a brand we do not know. Check the spelling against your photo.",
    }[status]
    if resolved:
        hint = "You looked at this line. Your decision is kept."
    return f"""<div class="flag flag--{state}" data-resolved="{str(resolved).lower()}">
  <div class="flag__top"><span class="flag__line">Line {line_no}</span>{chip("checked") if resolved else chip(status, suggestion)}</div>
  <p class="flag__text"><span class="mono">{escape(row['medicine'] or '(blank)')}</span> · {escape(row['dosage'])} · {escape(row['frequency'])}</p>
  <p class="flag__hint">{hint}</p></div>"""


def all_clear():
    return f'<div class="flag flag--verified">{chip("verified")}<p class="flag__hint">Every line matches a known medicine. Still glance at the table against your photo before confirming.</p></div>'


def confirm_hint(lines):
    if not lines:
        return '<p class="hint hint--ok">Every flagged line has a decision. You can confirm.</p>'
    which = ", ".join(str(n) for n in lines)
    return f'<p class="hint" role="status">Confirm unlocks after you fix or keep line{"s" if len(lines) > 1 else ""} {which}.</p>'


_FIELD = re.compile(r"\*\*(.+?):\*\*\s*(.*)")


def report(md):
    """Turn the report markdown ('## Name' + '**Label:** text' lines) into cards. None if it has no sections."""
    intro, *sections = re.split(r"^## ", md, flags=re.M)
    if not sections:
        return None
    cards = []
    for sec in sections:
        name, *lines = sec.strip().split("\n")
        fields = [m.groups() for m in map(_FIELD.match, lines) if m]
        head = {k: v for k, v in fields if k in ("Dose", "When")}
        body = "".join(
            f'<p class="med__note">{escape(v)}</p>' if k == "Note" else f"<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>"
            for k, v in fields if k not in head)
        cards.append(f"""<article class="med{' med--unknown' if 'Note' in dict(fields) else ''}">
  <header class="med__head"><h3>{escape(name)}</h3><p class="med__dose mono">{escape(head.get('Dose', ''))}</p>
  <p class="med__when">{escape(head.get('When', ''))}</p></header>
  <dl class="med__facts">{body}</dl></article>""")
    lead = escape(intro.replace("#", "").strip())
    return f'<section class="report" data-step="3"><p class="lede">{lead}</p><div class="meds">{"".join(cards)}</div></section>'


def chat_empty(n):
    return f'<p class="note">Ask anything about the {n} medicine{"s" if n != 1 else ""} above. Answers come only from the lines you confirmed.</p>'


DISCLAIMER = ("Scrivia helps you read a prescription. It does not diagnose, prescribe or replace your doctor. "
              "Before you start, stop or change any medicine, talk to your doctor or pharmacist.")


def disclaimer():
    return f"""<aside class="disclaimer" aria-label="Medical disclaimer"><p class="disclaimer__title">Not medical advice</p>
<p>{DISCLAIMER}</p><p class="disclaimer__privacy">Your photo is processed in memory and never stored.</p></aside>"""


def footer():
    return f'<footer class="foot"><p>{DISCLAIMER}</p></footer>'
