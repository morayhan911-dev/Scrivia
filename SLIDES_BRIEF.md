# NexCura / Scrivia: slide brief

NOTE: app code currently uses APP_NAME = "Scrivia" (app.py line 14, ui.py DISCLAIMER). prompt.md says the name is **NexCura**. Slides use NexCura. Change the constant before demo or the screenshots will say Scrivia.

## A. Facts to inject (all from the app)

**One-liner:** NexCura reads a prescription photo, makes a human verify every flagged line, and only then explains each medicine in plain English, with a chat limited to the verified lines.

**Problem (derive from app copy):** Handwritten prescriptions get misread. Look-alike drug names (Folvite vs Folite) are risky. Patients rarely understand what they were prescribed, how to take it, or what to watch for.

**Core differentiator:** AI is not trusted blindly. Step 2, the human verification gate, is the product. "AI read this, you confirm it." Confirm stays disabled until every flagged line is fixed or explicitly kept. Hint names the blocking lines: "Confirm unlocks after you fix or keep lines 1, 4."

**3-step flow**
1. Upload: photo (JPG/PNG/WEBP) -> "Read this prescription". Headline: "Know what your prescription says before you take it."
2. Check ("Check what we read"): "Read by the scanner: 4 lines" -> "Confirmed by you: 0 of 2 flagged lines checked". Photo beside flagged-line cards. Editable table (status, medicine, dose, how often). "Use Folvite" / "Keep as written" / "Add a missing line" / "Start over".
3. Understand ("Your prescription, in plain English"): one card per medicine (name, dose, when, what it is for, how to take it, tell your doctor if you notice). Chat with suggestion chips: "When do I take each one?", "Should I take these with food?", "What side effects should I watch for?", "What if I miss a dose?". Answers come only from confirmed lines. Off-topic gets: "I can only explain what is in your verified prescription..."

**Status chips (icon + text, never colour alone):** Verified, Did you mean X?, Unclear please check, Not recognised, Checked by you.

**Demo samples (fictional Greenleaf Family Clinic, Dr. S. Iyer, MBBS):**
- Sample 1 Fever, all clear: Dolo 650, Pan 40, Azithral 500, Cetzine.
- Sample 2 Look-alike trap: scanner reads "Folite" -> flagged "Did you mean Folvite?"; Ecosprin 75 frequency smudged -> "UNCLEAR - PLEASE VERIFY". Plus Shelcal 500, Thyronorm.
- Sample 3 Mixed: Glycomet 500, Telma 40, Atorva 10 verified; Zentrovix, Lumorin not recognised.

**Example report content (Sample 2):**
- Folvite: folic acid (vitamin B9), anaemia/pregnancy. Night, after food, 30 days.
- Thyronorm: levothyroxine, empty stomach 30-60 min before breakfast.
- Ecosprin 75: low-dose aspirin. Unreadable frequency -> "Ask your doctor or pharmacist before taking this."
- Unknown drug: "We have no notes for this name. Show this line to your pharmacist."

**Trust and safety:** Disclaimer on every screen: educational literacy tool, does not diagnose/prescribe, talk to doctor or pharmacist. Privacy: "Your photo is processed in memory and never stored." No account.

**Tech (slide for judges):** Streamlit (all logic: uploader, data_editor, chat, session_state). Custom HTML/CSS for design. Python: streamlit, pandas, pillow. Backend teammate: Gemini OCR + Groq/Llama. Frontend talks to the backend through a 4-function contract: extract_prescription, check_medicine, generate_report, chat_reply. Swapping stub for real backend = one import line. Demo Mode works fully offline (bundled fonts and images). Responsive and tested with Playwright at 390 / 768 / 1440 px, WCAG AA contrast, 44px tap targets, reduced-motion respected.

**Design system:** warm paper #FAF6EF, ink #1B222E, ballpoint blue #2953A5, highlighter yellow #FFE887 (marks what the human must check), check green #2B663E, brick red #A13029. Fonts: Newsreader (display serif), Geist (UI), Geist Mono (doses). No gradients, glow, glassmorphism, emoji icons or "AI magic" copy.

**Honest limits (put on a roadmap slide):** Backend is a stub with canned data until the teammate connects Gemini/Groq. Medicine knowledge base is tiny (11 meds). Hero image and sample prescription images are placeholders until generated (see IMAGE_PROMPTS.md). Not medical advice.

**Do not claim:** accuracy numbers, user counts, clinical validation, or regulatory approval. None exist.

## B. Images to attach for Claude Design

Screenshots (in verification/): `1440-s1-1-upload.png`, `1440-s2-2-check.png` (best slide, shows flags + disabled confirm), `1440-s2-2b-resolved.png`, `1440-s2-3-report.png` (also `1440-s3-3-report.png`), `1440-s3-2-check.png`, and mobile `390-s2-2-check.png`, `390-s2-3-report.png`.
Samples: `assets/samples/sample-2-lookalike.jpg`, `sample-1-fever.jpg`. Logo: `assets/logo-mark.png` if generated.
Caveat: current hero is a grey placeholder and sample slips are synthetic placeholders. Use screenshots after the real images are dropped in, or crop around the hero.

## C. Prompt for Claude Design

```
Create a 10-slide, 16:9 pitch deck for a hackathon demo of NexCura, a prescription explainer. Audience: hackathon judges (mixed technical/non-technical). Length: 4-5 minute talk. Use ONLY the facts below and the attached screenshots. Do not invent statistics, users, accuracy figures or awards.

VISUAL DIRECTION (match the product): warm paper background #FAF6EF, ink text #1B222E, ballpoint-blue accent #2953A5, highlighter-yellow #FFE887 used ONLY as a marker swipe behind the one phrase that matters on a slide, green #2B663E for "verified", brick #A13029 sparingly. Headlines in Newsreader (serif), body in Geist, doses/code in Geist Mono (Google Fonts are fine). Calm, clinical, editorial, generous whitespace, one idea per slide, max ~25 words of body text per slide. NO gradients, glows, glassmorphism, purple/blue "AI" look, robots/brains/circuit art, emoji icons, stock photos. Show the real UI: place the attached screenshots in clean frames (hairline #D9D4C9 border, 10px radius, no heavy shadows), crop to the relevant part, and add 1-2 plain callout labels with thin lines. Status chips must show icon + text, as in the app.

SLIDES
1. Title: "NexCura" + "Know what your prescription says before you take it." Screenshot: Step 1 upload (1440-s1-1-upload.png), cropped.
2. Problem: handwritten prescriptions get misread; look-alike names (Folvite / Folite) are risky; patients don't know what they were given or how to take it. No fake stats.
3. Idea: "AI reads. You confirm. Then it explains." A 3-step strip: Upload -> Check -> Understand, mirroring the app's progress indicator.
4. Step 1 Upload: photo in, one button "Read this prescription". Demo Mode with 3 fictional samples works offline.
5. Step 2 Check (CENTERPIECE, give it the most space): screenshot 1440-s2-2-check.png. Callouts: "Read by the scanner: 4 lines" -> "Confirmed by you: 0 of 2"; chip "Did you mean Folvite?"; chip "Unclear, please check"; disabled Confirm with "Confirm unlocks after you fix or keep lines 1, 4." Headline: "The human check is the product."
6. Trap demo: side by side the sample-2 prescription image and the flagged cards: scanner read "Folite" -> suggests "Folvite"; Ecosprin 75 frequency smudged -> "UNCLEAR - PLEASE VERIFY". Message: the AI is never trusted blindly.
7. Step 3 Understand: screenshot 1440-s2-3-report.png cropped to 2 medicine cards + chat chips. Callouts: one card per medicine (what it's for, how to take it, tell your doctor if...), chat answers only from confirmed lines, off-topic -> safe fallback.
8. Safety & trust: disclaimer on every screen, "processed in memory, never stored", unrecognised drugs say "Show this line to your pharmacist", unreadable lines never get a made-up schedule. Chip row showing all 4 status chips.
9. How it's built: Streamlit for all behavior, custom HTML/CSS for design, Gemini OCR + Groq/Llama backend (teammate), 4-function contract (extract_prescription, check_medicine, generate_report, chat_reply) so swapping stub -> real backend is one import line. Also: offline-capable, responsive 390/768/1440 (show 390-s2-2-check.png in a phone frame), WCAG AA, 44px tap targets, tested with Playwright.
10. Roadmap / honest status + close: done = full 3-step flow, verification gate, report, chat; next = connect real OCR/LLM, larger medicine database, multi-page prescriptions, regional languages. End line: "Not medical advice. A tool to help you ask your doctor better questions."

OUTPUT: editable slides (text as real text, not baked into images), consistent grid, speaker notes of 2-3 sentences per slide. Slide 5 and 6 are the emotional peak, so keep them uncluttered.
```
