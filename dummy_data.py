"""Canned demo data. Source of truth for the sample prescription images
(IMAGE_PROMPTS.md must match these lines exactly). Reports + chat added in M1."""

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

# check_medicine() lookup; anything absent -> "unrecognized".
KNOWN = {
    "dolo 650", "pan 40", "azithral 500", "cetzine", "folvite", "shelcal 500",
    "thyronorm", "ecosprin 75", "glycomet 500", "telma 40", "atorva 10",
}
LOOKALIKES = {"folite": "Folvite"}

# Plain-English notes used by generate_report() and chat_reply(): (what for, how to take, watch for).
MED_INFO = {
    "dolo 650": ("Paracetamol. Brings down fever and eases mild pain.",
                 "Take after food. Keep at least 4 to 6 hours between doses.",
                 "Do not take other paracetamol products alongside it. Avoid alcohol."),
    "pan 40": ("Pantoprazole. Lowers stomach acid and protects the stomach lining.",
               "Swallow whole, 30 to 60 minutes before breakfast.",
               "Headache or loose stools. Ask before using it for months at a time."),
    "azithral 500": ("Azithromycin, an antibiotic for bacterial infections.",
                     "Finish every dose, even if you feel better early.",
                     "Loose stools, nausea or stomach upset."),
    "cetzine": ("Cetirizine. Calms allergy symptoms like sneezing, runny nose and itching.",
                "Take at bedtime because it can make you sleepy.",
                "Drowsiness. Do not drive if you feel sleepy. Alcohol makes it worse."),
    "folvite": ("Folic acid (vitamin B9). Used for anaemia and during pregnancy.",
                "Take once a day, at the same time each day.",
                "Usually well tolerated. Tell your doctor about any rash."),
    "shelcal 500": ("Calcium with vitamin D3 for bone strength.",
                    "Take after food. Keep it 4 hours apart from a thyroid tablet.",
                    "Constipation or bloating."),
    "thyronorm": ("Levothyroxine. Replaces thyroid hormone your body is short of.",
                  "Take on an empty stomach, 30 to 60 minutes before breakfast, same time daily.",
                  "Fast heartbeat, sweating or weight loss can mean the dose is too high."),
    "ecosprin 75": ("Low-dose aspirin. Thins the blood to lower the risk of heart attack and stroke.",
                    "Take after food.",
                    "Unusual bleeding, black stools or stomach pain. Tell any dentist you take it."),
    "glycomet 500": ("Metformin. Lowers blood sugar in type 2 diabetes.",
                     "Take with or right after a meal.",
                     "Stomach upset or loose stools in the first weeks."),
    "telma 40": ("Telmisartan. Lowers blood pressure.",
                 "Take at the same time every day.",
                 "Dizziness when you stand up quickly."),
    "atorva 10": ("Atorvastatin. Lowers cholesterol.",
                  "Usually taken at night, with or without food.",
                  "Muscle pain or weakness you cannot explain."),
}

FALLBACK = ("I can only explain what is in your verified prescription. For anything else, "
            "including whether a medicine is right for you, please ask your doctor or pharmacist.")


def sample_for(filename):
    """Map an uploaded filename to a sample key, or None."""
    name = (filename or "").lower()
    return next((k for k, s in SAMPLES.items() if k in name or s["filename"].rsplit(".", 1)[0] in name), None)
