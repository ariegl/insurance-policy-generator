"""Export logic for PDF, JSON and Plain Text output.

Each function receives a list of policy dictionaries (as returned by
:class:`~py.data_generator.PolicyGenerator`) and returns the
corresponding export representation:

* ``export_pdf``       -> bytes (raw PDF file stream)
* ``export_json``      -> str   (pretty‑printed JSON)
* ``export_txt``       -> str   (human‑readable summary)
"""

from __future__ import annotations

import io
import json
import zipfile
from typing import Any, Dict, List


def export_pdf(policies: List[Dict[str, Any]]) -> bytes:
    """Render *policies* as a professional PDF document.

    Each policy appears on a new page with a formal letterhead,
    a structured data table, legal boilerplate, and a signature line.

    Returns the raw PDF binary content that can be turned into a
    browser Blob and downloaded.
    """
    from fpdf import FPDF  # delayed import keeps module lightweight

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for idx, policy in enumerate(policies, start=1):
        # ---------- letterhead ----------
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Agnostic Global Insurance Co.",
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(0, 5, "Policy Certificate - Full Coverage",
                 new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # ---------- identification block ----------
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Policy ID:     {policy.get('policy_id','')}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Holder Name:   {policy.get('holder_name','')}",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # ---------- data table ----------
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Coverage Details", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)

        col1 = 70     # label column width
        col2 = pdf.epw - col1  # value column width

        for field, value in policy.items():
            if field in ("policy_id", "holder_name"):
                continue
            label = field.replace("_", " ").title()
            pdf.cell(col1, 7, label, border=1, align="L")
            pdf.cell(col2, 7, str(value), border=1, align="L")
            pdf.ln(7)

        pdf.ln(5)

        # ---------- legal boilerplate ----------
        pdf.set_font("Helvetica", "I", 8)
        boilerplate = (
            "This certificate is issued subject to the terms and conditions "
            "contained in the Policy Contract. Please read the policy document "
            "carefully to understand the scope of coverage, exclusions, and "
            "obligations. This document does not constitute an insurance contract "
            "unless accompanied by the complete policy wording."
        )
        pdf.multi_cell(0, 5, boilerplate, align="L")
        pdf.ln(4)

        # ---------- signature block ----------
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7,
                 "Authorized Representative Signature: _________________________",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font("Helvetica", "I", 8)
        pdf.cell(0, 5, "Date of Issue: ___________   Policy Period: ___________",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)

        # start a new page for the next policy unless it's the last one
        if idx < len(policies):
            pdf.add_page()

    return pdf.output()


def export_zip(policies: List[Dict[str, Any]]) -> bytes:
    """Bundle each policy as an individual PDF file inside a ZIP archive.

    The filename inside the archive follows the pattern ``Policy_<policy_id>.pdf``.
    Returns the raw bytes of the ZIP file.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, policy in enumerate(policies):
            # Generate a single‑policy PDF
            single_pdf = export_pdf([policy])  # bytes
            policy_id = policy.get("policy_id", f"{idx + 1}")
            filename = f"Policy_{policy_id}.pdf"
            zf.writestr(filename, single_pdf)
    return buf.getvalue()


def export_json(policies: List[Dict[str, Any]]) -> str:
    """Pretty‑print the list of policies as a JSON string."""
    return json.dumps(policies, indent=2, ensure_ascii=False)


def export_txt(policies: List[Dict[str, Any]]) -> str:
    """Create a readable plain‑text summary of all generated policies."""
    lines: List[str] = []
    for idx, policy in enumerate(policies, start=1):
        lines.append(f"--- Policy #{idx} ---")
        for field, value in policy.items():
            label = field.replace("_", " ").title()
            lines.append(f"  {label}: {value}")
        lines.append("")  # blank line between entries
    return "\n".join(lines)
