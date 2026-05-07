"""Export logic for PDF, JSON and Plain Text output.

Each function receives a list of policy dictionaries (as returned by
:class:`~py.data_generator.PolicyGenerator`) and returns the
corresponding export representation:

* ``export_pdf``       -> bytes (raw PDF file stream)
* ``export_json``      -> str   (pretty‑printed JSON)
* ``export_txt``       -> str   (human‑readable summary)
"""

from __future__ import annotations

import json
from typing import Any, Dict, List


def export_pdf(policies: List[Dict[str, Any]]) -> bytes:
    """Render *policies* as a professional PDF page using fpdf2.

    Returns the raw PDF binary content that can be turned into a
    browser Blob and downloaded.
    """
    from fpdf import FPDF  # delayed import keeps module lightweight

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    for idx, policy in enumerate(policies, start=1):
        # Section header
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"Policy #{idx}", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("Helvetica", size=10)

        # Policy ID
        pdf.cell(0, 6, f"Policy ID:        {policy.get('policy_id', '')}",
                 new_x="LMARGIN", new_y="NEXT")
        # Holder Name
        pdf.cell(0, 6, f"Holder Name:      {policy.get('holder_name', '')}",
                 new_x="LMARGIN", new_y="NEXT")

        # Remaining fields printed in the same style
        for field, value in policy.items():
            if field in ("policy_id", "holder_name"):
                continue  # already shown above
            # Format the field label
            label = field.replace("_", " ").title()
            pdf.cell(0, 6, f"{label}: {value}",
                     new_x="LMARGIN", new_y="NEXT")

        # Blank separator between policies
        pdf.ln(4)

    # Return raw bytes
    return pdf.output(dest="S").encode("latin-1")


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
