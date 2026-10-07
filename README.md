# Scrivia

Scrivia reads a photo of a doctor's prescription and explains it in plain English. You take a picture of the slip, check every line it read, and then get a short note on each medicine plus a chat box for follow-up questions.

Handwritten prescriptions are hard to read, for people and for software. So Scrivia never skips the checking step: it won't explain anything until you've looked at what it read.

## How it works

1. Upload. Gemini reads the photo and pulls out each medicine, its dose and how often to take it. If it can't make out a word, it writes UNCLEAR instead of guessing.
2. Check. Each name is spell-checked against a list of common Indian brands and the 150 most prescribed generics. A name on the list goes straight through. Anything else gets flagged so you can confirm it against your slip, and likely misreads come with a suggestion (say, "Folite" when the slip says Folvite). The Confirm button stays locked until you've dealt with every flagged line, and you can edit any cell in the table.
3. Understand. Groq looks up every confirmed medicine, whether it matched the list or you confirmed it yourself, and writes a short note on each one: what it's usually for, precautions, common side effects and when to see a doctor. You can open the report as a PDF or download it, and ask questions in the chat.

The chat only knows about the prescription in front of it. Its memory lives in your browser session and disappears when you close the tab or start over. Nothing gets written to disk.

## Running it locally

You need Python 3.11 or newer. We built it on Windows with Python 3.14.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Then create a file called `backend/env` with your two API keys:

```
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
```

Both have free tiers. You can get a Gemini key at https://aistudio.google.com/apikey and a Groq key at https://console.groq.com/keys. The file is gitignored, so it won't end up on GitHub by accident.

Start the app:

```
streamlit run app.py
```

It opens at http://localhost:8501. If you don't have a prescription handy, leave Demo mode on in the sidebar and pick one of the three sample slips.

If you want different models, set `GEMINI_MODEL` or `GROQ_MODEL` in the same file. The defaults are `gemini-3.1-flash-lite` (with two fallbacks if it's busy) and `openai/gpt-oss-120b`.

## Deploying

On Streamlit Community Cloud, point a new app at this repo with `app.py` as the main file, then paste the two keys into the app's Secrets settings in this form:

```
GEMINI_API_KEY = "..."
GROQ_API_KEY = "..."
```

## Where things are

| File | What it does |
|---|---|
| `app.py` | The three steps and the page layout |
| `ui.py`, `styles.css` | HTML pieces and all the styling |
| `backend/backend_ocr.py` | Sends the photo to Gemini, using the rules in `PRESCRIPTION-OCR.txt` |
| `backend/backend_groq.py` | Groq calls for medicine notes and chat; the prompts live in `PRESCRIPTION-HELPER.txt` |
| `backend/report_generator.py`, `backend/report.py` | The written report and its PDF version |
| `backend/safety.py` | Name checking, and turning "1-0-1" into "morning and night" |
| `backend/spellcheck/` | The list of 150 common generics |
| `dummy_data.py`, `assets/samples/` | The demo prescriptions |

`python backend/safety.py` runs a quick self-check and prints `ok`.

## Things worth knowing

Groq's free tier allows 8,000 tokens a minute. A report for five medicines uses about half of that, so if you generate two reports back to back the second one may pause for a few seconds while the app waits for the limit to reset.

Gemini's speed varies a lot from minute to minute. Reading a photo usually takes somewhere between 3 and 13 seconds.

The name lists only exist to save clicks and catch spelling slips. A name that isn't on them still works: you confirm it, and Groq looks it up. If Groq doesn't recognise a name, the report says so instead of guessing.

On Gemini's free tier, Google may use uploaded images to improve its models. Prescriptions are health records, so switch to a paid key before real patients use this.

## Not medical advice

Scrivia helps you read a prescription. It doesn't diagnose, prescribe or replace your doctor or pharmacist. Talk to them before you start, stop or change any medicine.
