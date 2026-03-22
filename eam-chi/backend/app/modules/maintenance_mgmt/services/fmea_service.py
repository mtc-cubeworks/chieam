"""
FMEA Analysis Service (MW-7)
==============================
Failure Mode and Effects Analysis methods:
- 5-Why Root Cause Analysis
- Fishbone (Ishikawa) Diagram categories
- RPN (Risk Priority Number) calculation
"""
from app.application.server_actions.registry import server_actions


# Fishbone default categories for maintenance failure analysis
FISHBONE_CATEGORIES = [
    "Man (People)",
    "Machine (Equipment)",
    "Material",
    "Method (Process)",
    "Measurement",
    "Mother Nature (Environment)",
]


def calculate_rpn(severity: int, occurrence: int, detection: int) -> int:
    """
    Calculate Risk Priority Number.
    RPN = Severity × Occurrence × Detection
    Each factor is scored 1–10.
    """
    s = max(1, min(10, severity or 1))
    o = max(1, min(10, occurrence or 1))
    d = max(1, min(10, detection or 1))
    return s * o * d


@server_actions.register("failure_analysis", "Calculate RPN")
async def calculate_rpn_action(doc, ctx):
    """
    MW-7: Calculate the Risk Priority Number for a failure analysis record.
    Updates severity_score, occurrence_score, detection_score, and rpn fields.
    """
    from app.services.document import save_doc

    severity = int(getattr(doc, "severity_score", 1) or 1)
    occurrence = int(getattr(doc, "occurrence_score", 1) or 1)
    detection = int(getattr(doc, "detection_score", 1) or 1)

    rpn = calculate_rpn(severity, occurrence, detection)
    doc.rpn = rpn

    # Classify risk level
    if rpn >= 200:
        doc.risk_level = "Critical"
    elif rpn >= 120:
        doc.risk_level = "High"
    elif rpn >= 80:
        doc.risk_level = "Medium"
    else:
        doc.risk_level = "Low"

    await save_doc(doc, ctx.db)

    return {
        "status": "success",
        "message": f"RPN calculated: {rpn} ({doc.risk_level})",
    }


@server_actions.register("failure_analysis", "Generate 5-Why Template")
async def generate_five_why_template(doc, ctx):
    """
    MW-7: Generate a structured 5-Why analysis template
    and store it in the analysis_notes field.
    """
    from app.services.document import save_doc

    failure_mode = getattr(doc, "failure_mode", "") or "Unknown failure"
    template = (
        f"5-Why Root Cause Analysis\n"
        f"{'=' * 40}\n"
        f"Problem Statement: {failure_mode}\n\n"
        f"Why 1: \n"
        f"Why 2: \n"
        f"Why 3: \n"
        f"Why 4: \n"
        f"Why 5: \n\n"
        f"Root Cause: \n"
        f"Corrective Action: \n"
        f"Preventive Action: \n"
    )

    existing_notes = getattr(doc, "analysis_notes", "") or ""
    if existing_notes:
        doc.analysis_notes = existing_notes + "\n\n" + template
    else:
        doc.analysis_notes = template

    await save_doc(doc, ctx.db)

    return {
        "status": "success",
        "message": "5-Why analysis template generated",
    }


@server_actions.register("failure_analysis", "Generate Fishbone Template")
async def generate_fishbone_template(doc, ctx):
    """
    MW-7: Generate a Fishbone (Ishikawa) diagram template
    with the 6M categories.
    """
    from app.services.document import save_doc

    failure_mode = getattr(doc, "failure_mode", "") or "Unknown failure"
    lines = [
        f"Fishbone (Ishikawa) Diagram Analysis",
        f"{'=' * 40}",
        f"Effect: {failure_mode}",
        "",
    ]
    for category in FISHBONE_CATEGORIES:
        lines.append(f"--- {category} ---")
        lines.append("  • Cause 1: ")
        lines.append("  • Cause 2: ")
        lines.append("")

    lines.extend(["Primary Root Cause: ", "Recommended Action: "])
    template = "\n".join(lines)

    existing_notes = getattr(doc, "analysis_notes", "") or ""
    if existing_notes:
        doc.analysis_notes = existing_notes + "\n\n" + template
    else:
        doc.analysis_notes = template

    await save_doc(doc, ctx.db)

    return {
        "status": "success",
        "message": "Fishbone analysis template generated",
    }
