"""Canned demo data. Source of truth for the sample prescription images
(IMAGE_PROMPTS.md must match these lines exactly). Used only for the demo-mode photos."""

SAMPLES = {
    "fever": {
        "label": "Sample 1: Fever, all clear",
        "filename": "sample-1-fever.jpg",
        "rows": [
            {"medicine": "Dolo 650", "dosage": "650 mg tablet", "frequency": "1-1-1 after food, 3 days"},
            {"medicine": "Pan 40", "dosage": "40 mg tablet", "frequency": "1-0-0 before breakfast, 5 days"},
            {"medicine": "Azithral 500", "dosage": "500 mg tablet", "frequency": "1-0-0 after food, 3 days"},
            {"medicine": "Cetzine", "dosage": "10 mg tablet", "frequency": "0-0-1 at bedtime, 5 days"},
        ],
    },
    "lookalike": {
        "label": "Sample 2: Look-alike drug trap",
        "filename": "sample-2-lookalike.jpg",
        # "Folite" is the OCR misread of the handwritten "Folvite" on the image.
        "rows": [
            {"medicine": "Folite", "dosage": "5 mg tablet", "frequency": "0-0-1 after food, 30 days"},
            {"medicine": "Shelcal 500", "dosage": "500 mg tablet", "frequency": "1-0-1 after food, 30 days"},
            {"medicine": "Thyronorm", "dosage": "50 mcg tablet", "frequency": "1-0-0 empty stomach, 30 days"},
            {"medicine": "Ecosprin 75", "dosage": "75 mg tablet", "frequency": "UNCLEAR - PLEASE VERIFY"},
        ],
    },
    "mixed": {
        "label": "Sample 3: Some names not recognised",
        "filename": "sample-3-mixed.jpg",
        "rows": [
            {"medicine": "Glycomet 500", "dosage": "500 mg tablet", "frequency": "1-0-1 after food, 30 days"},
            {"medicine": "Telma 40", "dosage": "40 mg tablet", "frequency": "1-0-0 morning, 30 days"},
            {"medicine": "Zentrovix", "dosage": "10 mg tablet", "frequency": "0-0-1 at night, 15 days"},
            {"medicine": "Atorva 10", "dosage": "10 mg tablet", "frequency": "0-0-1 at night, 30 days"},
            {"medicine": "Lumorin", "dosage": "5 ml syrup", "frequency": "1-0-1, 7 days"},
        ],
    },
}

def sample_for(filename):
    """Map an uploaded filename to a sample key, or None."""
    name = (filename or "").lower()
    return next((k for k, s in SAMPLES.items() if k in name or s["filename"].rsplit(".", 1)[0] in name), None)
