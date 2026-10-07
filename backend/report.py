import io
from datetime import date
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import safety

# ---------------------------------------------------------------------
# HOW TO USE (for the back-end developer)
#
#   pdf_bytes = report.make_pdf(data, checks, summary, infos)
#
#   data    : the confirmed prescription dictionary (same as before)
#   checks  : list of safety.check_medicine(...) results, same order as data["medicines"]
#   summary : plain text summary
#   infos   : OPTIONAL list, same order as data["medicines"]. Each item is a dictionary
#             (or None) like this:
#               {
#                 "source": "list" or "general" or "unconfirmed",
#                 "recognised": True,
#                 "used_for": "Fever and mild pain",
#                 "precautions": ["...", "..."],
#                 "common_side_effects": ["...", "..."],
#                 "see_a_doctor_if": ["...", "..."],
#               }
#             "list"        = medicine is in our verified CSV list
#             "general"     = patient confirmed the name, information came from the AI's own knowledge
#             "unconfirmed" = the name was not confirmed (or the AI did not recognise it), so no details are shown
#
# If infos is left out, the report still works (it shows the CSV use / side effects).
# Empty details are never printed: a prescription with only medicine names gives a short report.
# ---------------------------------------------------------------------

SOURCE_LINES = {
    "list": "Source: Scrivia medicine lookup",
    "general": "Source: AI general knowledge. NOT checked against our list - please confirm with your pharmacist.",
    "unconfirmed": "We could not find this medicine, so no details are given. Please ask your pharmacist.",
}

LIGHT_RED = colors.Color(1, 0.9, 0.9)
LIGHT_YELLOW = colors.Color(1, 0.97, 0.85)


def safe(text):
    # reportlab reads < and & as markup, so we escape them first.
    if text is None:
        return ""
    return escape(str(text))


def as_list(value):
    # Turns a list (or a single piece of text) into a clean list of non-empty texts.
    result = []
    if isinstance(value, list):
        for item in value:
            if str(item).strip() != "":
                result.append(str(item).strip())
    elif value is not None and str(value).strip() != "":
        result.append(str(value).strip())
    return result


def any_value(medicines, key):
    for med in medicines:
        if str(med.get(key, "")).strip() != "":
            return True
    return False


def get_info(infos, index):
    if infos is None:
        return None
    if index < len(infos):
        return infos[index]
    return None


def source_of(info, check):
    # Decides where the information about one medicine came from.
    if info is not None:
        if info.get("recognised", True) is False:
            return "unconfirmed"
        source = str(info.get("source", ""))
        if source in SOURCE_LINES:
            return source
    if check["status"] == "verified":
        return "list"
    return "unconfirmed"


def check_text(source, check):
    if source == "list":
        return "Name matched our list" if check["status"] == "verified" else "Name confirmed by you"
    if source == "general":
        return "Confirmed by you - not in our list"
    if check["status"] == "suggest":
        return "Looks like " + check["suggestion"] + " - please verify"
    return "Not found - ask your pharmacist"


def add_list(parts, title, items, style, bullet_style):
    if len(items) == 0:
        return
    parts.append(Paragraph("<b>" + title + ":</b>", style))
    for item in items:
        parts.append(Paragraph("- " + safe(item), bullet_style))


def medicine_block(med, check, info, source, styles, bullet_style):
    small = styles["Normal"]
    parts = []

    title = "<b>" + safe(med["name"]) + "</b>"
    if check.get("generic", "") != "" and source != "unconfirmed":
        if not str(med["name"]).strip().lower().startswith(check.get("generic", "").strip().lower()):
            title = title + " (" + safe(check.get("generic", "")) + ")"
    parts.append(Paragraph(title, styles["Heading3"]))

    used_for = ""
    precautions = []
    side_effects = []
    see_doctor = []
    if info is not None and source != "unconfirmed":
        used_for = str(info.get("used_for", "")).strip()
        precautions = as_list(info.get("precautions"))
        side_effects = as_list(info.get("common_side_effects"))
        see_doctor = as_list(info.get("see_a_doctor_if"))
    elif info is None and source == "list":
        used_for = check.get("use", "")
        side_effects = as_list(check.get("side_effects"))

    nothing_to_show = used_for == "" and len(precautions) == 0 and len(side_effects) == 0 and len(see_doctor) == 0
    if nothing_to_show:
        if source == "unconfirmed":
            parts.append(Paragraph(safe(SOURCE_LINES["unconfirmed"]), small))
        else:
            parts.append(Paragraph("No details available. Please ask your pharmacist.", small))
    else:
        if used_for != "":
            parts.append(Paragraph("<b>Used for:</b> " + safe(used_for), small))
        add_list(parts, "Precautions", precautions, small, bullet_style)
        add_list(parts, "Common side effects", side_effects, small, bullet_style)
        add_list(parts, "See a doctor if", see_doctor, small, bullet_style)
        parts.append(Paragraph("<i>" + safe(SOURCE_LINES[source]) + "</i>", small))
    parts.append(Spacer(1, 8))
    return KeepTogether(parts)


def make_pdf(data, checks, summary, infos=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm,
                            title="Scrivia prescription report", author="Scrivia")
    styles = getSampleStyleSheet()
    small = styles["Normal"]
    bullet_style = ParagraphStyle("bullet_small", parent=small, leftIndent=14)
    medicines = data["medicines"]
    story = []

    story.append(Paragraph("Prescription Summary Report", styles["Title"]))
    story.append(Paragraph("Generated on " + date.today().strftime("%d %B %Y"), small))
    story.append(Spacer(1, 12))

    # ---------- header details: only the ones that are really written ----------
    header_rows = []
    patient_text = str(data.get("patient_name", "")).strip()
    extras = []
    if str(data.get("age", "")).strip() != "":
        extras.append("age " + str(data["age"]).strip())
    if str(data.get("gender", "")).strip() != "":
        extras.append(str(data["gender"]).strip())
    if len(extras) > 0:
        if patient_text != "":
            patient_text = patient_text + " (" + ", ".join(extras) + ")"
        else:
            patient_text = ", ".join(extras)
    if patient_text != "":
        header_rows.append(["Patient", patient_text])
    if str(data.get("doctor_name", "")).strip() != "":
        header_rows.append(["Doctor", str(data["doctor_name"]).strip()])
    if str(data.get("date", "")).strip() != "":
        header_rows.append(["Prescription date", str(data["date"]).strip()])
    if str(data.get("diagnosis", "")).strip() != "":
        header_rows.append(["Diagnosis", str(data["diagnosis"]).strip()])

    if len(header_rows) > 0:
        table_rows = []
        for row in header_rows:
            table_rows.append([Paragraph("<b>" + safe(row[0]) + "</b>", small), Paragraph(safe(row[1]), small)])
        header_table = Table(table_rows, colWidths=[4 * cm, 14 * cm])
        header_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 14))

    # ---------- medicines table: only columns that have something in them ----------
    story.append(Paragraph("Medicines", styles["Heading2"]))

    optional_columns = [
        ("strength", "Strength", 2.4),
        ("frequency", "How often", 5.0),
        ("duration", "Duration", 2.2),
        ("instructions", "Instructions", 2.6),
    ]
    shown = []
    shown_width = 0.0
    for column in optional_columns:
        if any_value(medicines, column[0]):
            shown.append(column)
            shown_width = shown_width + column[2]
    extra = 10.0 - shown_width
    medicine_width = 3.8 + extra / 2
    check_width = 4.2 + extra / 2

    header_row = [Paragraph("<b>Medicine</b>", small)]
    widths = [medicine_width * cm]
    for column in shown:
        header_row.append(Paragraph("<b>" + column[1] + "</b>", small))
        widths.append(column[2] * cm)
    header_row.append(Paragraph("<b>Check</b>", small))
    widths.append(check_width * cm)
    rows = [header_row]

    sources = []
    index = 0
    for med in medicines:
        check = checks[index]
        info = get_info(infos, index)
        source = source_of(info, check)
        sources.append(source)
        index = index + 1

        row = [Paragraph(safe(med["name"]), small)]
        for column in shown:
            value = str(med.get(column[0], "")).strip()
            if column[0] == "frequency" and value != "":
                words = safety.explain_frequency(value)
                if words != value:
                    value = value + " (" + words + ")"
            row.append(Paragraph(safe(value), small))
        row.append(Paragraph(safe(check_text(source, check)), small))
        rows.append(row)

    if len(medicines) == 0:
        story.append(Paragraph("No medicines were found in this prescription.", small))
    else:
        med_table = Table(rows, colWidths=widths, repeatRows=1)
        style_list = [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
        row_number = 1
        for source in sources:
            if source == "unconfirmed":
                style_list.append(("BACKGROUND", (0, row_number), (-1, row_number), LIGHT_RED))
            elif source == "general":
                style_list.append(("BACKGROUND", (0, row_number), (-1, row_number), LIGHT_YELLOW))
            row_number = row_number + 1
        med_table.setStyle(TableStyle(style_list))
        story.append(med_table)
        story.append(Spacer(1, 6))

        if not any_value(medicines, "frequency") and not any_value(medicines, "duration"):
            story.append(Paragraph(
                "<i>This prescription does not say how often or for how long to take each medicine. "
                "Please ask your doctor or pharmacist.</i>", small))
        story.append(Spacer(1, 10))

    # ---------- about each medicine ----------
    if len(medicines) > 0:
        story.append(Paragraph("About your medicines", styles["Heading2"]))
        index = 0
        for med in medicines:
            check = checks[index]
            info = get_info(infos, index)
            story.append(medicine_block(med, check, info, sources[index], styles, bullet_style))
            index = index + 1
        story.append(Spacer(1, 6))

    # ---------- plain-language summary ----------
    if str(summary).strip() != "":
        story.append(Paragraph("Summary in simple words", styles["Heading2"]))
        for line in str(summary).split("\n"):
            if line.strip() != "":
                story.append(Paragraph(safe(line), small))
                story.append(Spacer(1, 4))
        story.append(Spacer(1, 10))

    # ---------- doctor's advice and unclear parts (only if present) ----------
    if str(data.get("advice", "")).strip() != "":
        story.append(Paragraph("Doctor's advice", styles["Heading2"]))
        story.append(Paragraph(safe(data["advice"]), small))
        story.append(Spacer(1, 10))

    unclear = as_list(data.get("unclear_parts"))
    if len(unclear) > 0:
        story.append(Paragraph("Parts that were hard to read", styles["Heading2"]))
        for part in unclear:
            story.append(Paragraph("- " + safe(part), small))
        story.append(Spacer(1, 10))

    # ---------- questions to ask ----------
    story.append(Paragraph("Good questions to ask your doctor or pharmacist", styles["Heading2"]))
    questions = [
        "What is each medicine for, and what should I watch out for?",
        "Should I take it before or after food?",
        "What should I do if I miss a dose?",
        "When should I come back if I do not feel better?",
    ]
    for question in questions:
        story.append(Paragraph("- " + question, small))
    story.append(Spacer(1, 16))

    story.append(Paragraph("<i>" + safe(safety.DISCLAIMER) + "</i>", small))

    doc.build(story)
    return buffer.getvalue()
