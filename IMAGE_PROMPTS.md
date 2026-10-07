# Scrivia image prompts

Paste each prompt into your image model. Save with the exact filename into the path shown.
Until your files arrive the app uses neutral placeholders at the same aspect ratios, and a CSS/typographic wordmark replaces the logo.

## Shared palette and style (referenced below as STYLE)

Warm paper `#FAF6EF`, raised paper `#FEFDF9`, hairline `#D9D4C9`, ink blue-black `#1B222E`, ballpoint blue `#2953A5`, highlighter yellow `#FFE887`, check green `#2B663E`, brick red `#A13029` (sparingly).
Look: hand-inked editorial line illustration, single-weight ballpoint lines in `#1B222E` and `#2953A5`, flat fills from the palette, one highlighter-yellow `#FFE887` swipe as the only bright accent, subtle paper grain, generous empty space, calm and human.

**Base negative prompt (append to every one):** purple, violet, neon, gradient background, glow, lens flare, glassmorphism, 3D render, plastic, glossy, bokeh, sparkles, particles, robot, brain, circuit lines, holograms, stock-photo people, cartoon mascot, emoji, watermark, signature, extra text, gibberish lettering, blurry, noisy JPEG artifacts.

---

## 1. Logo mark
- File: `logo-mark.png` -> `assets/logo-mark.png`
- Size 1024x1024, 1:1, PNG with transparent background
- Prompt: Minimal logo mark on a transparent background. A small rounded-rectangle paper slip outline drawn in ink `#1B222E`, with a single short highlighter swipe in `#FFE887` across it and a crisp check mark in ballpoint blue `#2953A5` on top of the swipe. Flat vector, two line weights max, centered, lots of padding, reads clearly at 32px. STYLE.
- Negative: base + letters, words, pills, capsules, medical cross, caduceus, stethoscope, heart.

## 2. Favicon
- File: `favicon.png` -> `assets/favicon.png`
- Size 512x512, 1:1, PNG transparent
- Prompt: Same mark as logo-mark but simplified for 16 to 32px: thick check in `#2953A5` over a `#FFE887` swipe, no paper outline, no thin lines. Flat vector. STYLE.
- Negative: base + thin lines, small details, letters.

## 3. Hero illustration
- File: `hero.png` -> `assets/hero.png`
- Size 1600x1200, 4:3, PNG (opaque `#FAF6EF` background is fine)
- Prompt: Editorial ink illustration, top-down view of a kitchen table: a handwritten paper prescription slip, a strip of tablets, a reading pair of glasses, and a hand holding a highlighter that has just marked one line of the slip in `#FFE887`. Lines in `#1B222E`, small accents in `#2953A5`, background `#FAF6EF`. Composition weighted to the right with empty space on the left third. Handwriting on the slip is abstract squiggles, not readable words. STYLE.
- Negative: base + readable text on paper, faces, hospital, doctor in coat, phone screen UI, pill bottle labels.

## 4. Upload empty state
- File: `upload-empty.png` -> `assets/upload-empty.png`
- Size 800x600, 4:3, PNG transparent
- Prompt: Small spot illustration: a folded paper prescription slip sliding into an open rectangle tray drawn with a dashed `#2953A5` outline, one tiny `#FFE887` highlighter mark on the slip. Very few lines, lots of transparent space. STYLE.
- Negative: base + cloud icon, arrow icon, folder icon, readable text.

## 5. Error state
- File: `error.png` -> `assets/error.png`
- Size 600x450, 4:3, PNG transparent
- Prompt: Small spot illustration: a crumpled, unreadable paper slip with a single question mark drawn in brick `#A13029` beside it, ink lines `#1B222E`. Calm, not alarming. STYLE.
- Negative: base + warning triangle, skull, fire, red background, sad face.

## 6 to 8. Synthetic sample prescriptions (fictional, no real person data)

Common to all three:
- Size 1200x1600, 3:4, JPG, opaque
- Prompt prefix: Photograph-style flat scan of a fictional Indian outpatient prescription on off-white paper `#FEFDF9`, lit evenly from above, slight paper texture, slightly tilted 2 degrees. Printed letterhead at top reads only "Greenleaf Family Clinic" with a simple leaf line icon, and below it a printed line "Dr. S. Iyer, MBBS (fictional)". Large "Rx" symbol on the left. Medicine lines below are handwritten in blue ballpoint `#2953A5`, natural doctor handwriting but legible, one medicine per line, numbered 1, 2, 3. No patient name, no address, no phone, no registration number, no signature, no stamp. Write EXACTLY these lines and nothing else:
- Negative: base + any extra medicine lines, patient name, address, phone number, QR code, barcode, real hospital logo, signature, stamp, typed medicine lines.

### 6. `sample-1-fever.jpg` -> `assets/samples/sample-1-fever.jpg`
```
1. Dolo 650   650 mg tab   1-1-1 after food x 3 days
2. Pan 40   40 mg tab   1-0-0 before breakfast x 5 days
3. Azithral 500   500 mg tab   1-0-0 after food x 3 days
4. Cetzine   10 mg tab   0-0-1 at bedtime x 5 days
```
Extra: clean, tidy handwriting.

### 7. `sample-2-lookalike.jpg` -> `assets/samples/sample-2-lookalike.jpg`
```
1. Folvite   5 mg tab   0-0-1 after food x 30 days
2. Shelcal 500   500 mg tab   1-0-1 after food x 30 days
3. Thyronorm   50 mcg tab   1-0-0 empty stomach x 30 days
4. Ecosprin 75   75 mg tab   [frequency smudged]
```
Extra: on line 1 the "v" in "Folvite" is written faintly and nearly closed, so it could be misread as "Folite". On line 4 a small blue ink smudge covers the frequency so it cannot be read; the name and "75 mg tab" stay legible.

### 8. `sample-3-mixed.jpg` -> `assets/samples/sample-3-mixed.jpg`
```
1. Glycomet 500   500 mg tab   1-0-1 after food x 30 days
2. Telma 40   40 mg tab   1-0-0 morning x 30 days
3. Zentrovix   10 mg tab   0-0-1 at night x 15 days
4. Atorva 10   10 mg tab   0-0-1 at night x 30 days
5. Lumorin   5 ml syrup   1-0-1 x 7 days
```
Extra: slightly rushed handwriting, still legible.

---

## What you must generate (8 files)
`assets/logo-mark.png`, `assets/favicon.png`, `assets/hero.png`, `assets/upload-empty.png`, `assets/error.png`, `assets/samples/sample-1-fever.jpg`, `assets/samples/sample-2-lookalike.jpg`, `assets/samples/sample-3-mixed.jpg`.
Skipped on purpose: chat avatar (typographic initial instead), report header art (typography carries it). If generated prescription text differs from these lines, tell me and I update `dummy_data.py`.
