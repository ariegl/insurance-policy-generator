"""
Integration logic for the Agnostic Policy Generator.

Connects the HTML UI to Python backend via PyScript/Pyodide bridge.
Handles: generating policies, preview, download buttons for PDF, JSON, TXT.
"""

from __future__ import annotations

import traceback

from pyodide.ffi import create_proxy
from js import document, window, Uint8Array, Blob, URL

from py.data_generator import PolicyGenerator
from py.exporters import export_pdf, export_json, export_txt

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

_generator = PolicyGenerator()
_generated_policies = None  # persists between generate and download calls

# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------

def _generate_policies():
    """Read UI fields, delegate to PolicyGenerator, return list or None."""
    policy_type = document.querySelector("#policy-type").value
    if not policy_type:
        window.alert("Please select a policy type.")
        return None

    quantity_str = document.querySelector("#quantity").value
    try:
        quantity = int(quantity_str)
    except (ValueError, TypeError):
        window.alert("Quantity must be a number.")
        return None

    if quantity < 1 or quantity > 500:
        window.alert("Quantity must be between 1 and 500.")
        return None

    return _generator.generate_batch(policy_type, quantity)


def _update_preview(policies):
    """Fill the #preview-area div with a brief summary of the generated data."""
    preview_div = document.querySelector("#preview-area")
    if not policies:
        preview_div.innerHTML = "<p class='text-gray-400 text-sm'>No policies generated.</p>"
        return

    # Show up to three policies to keep the preview responsive
    lines = []
    for idx, policy in enumerate(policies[:3], start=1):
        lines.append(f"<strong>Policy #{idx}</strong><br/>")
        for field, value in policy.items():
            label = field.replace("_", " ").title()
            lines.append(f"<span>{label}: {value}</span><br/>")
        lines.append("<hr/>")
    lines.append(f"<em>… {len(policies)} total policies generated.</em>")
    preview_div.innerHTML = "\n".join(lines)

# ---------------------------------------------------------------------------
# Download helpers
# ---------------------------------------------------------------------------

def _download_blob(data, mime_type: str, filename: str):
    """Create a Blob, attach it to a hidden <a> element, and trigger download."""
    if isinstance(data, str):
        # For JSON/TXT – data is already a plain string
        blob = Blob.new([data], {"type": mime_type})
    else:
        # For PDF – data is raw bytes, convert to JS typed array
        uint8 = Uint8Array.new(list(data))
        blob = Blob.new([uint8], {"type": mime_type})

    url = URL.createObjectURL(blob)
    anchor = document.createElement("a")
    anchor.href = url
    anchor.download = filename
    document.body.appendChild(anchor)
    anchor.click()
    document.body.removeChild(anchor)
    URL.revokeObjectURL(url)

def download_pdf(event) -> None:
    """Handler for 'Download PDF' button."""
    if _generated_policies is None:
        return
    data = export_pdf(_generated_policies)               # bytes
    _download_blob(data, "application/pdf", "policies.pdf")

def download_json(event) -> None:
    """Handler for 'Download JSON' button."""
    if _generated_policies is None:
        return
    data = export_json(_generated_policies)               # str
    _download_blob(data, "application/json", "policies.json")

def download_txt(event) -> None:
    """Handler for 'Download TXT' button."""
    if _generated_policies is None:
        return
    data = export_txt(_generated_policies)                # str
    _download_blob(data, "text/plain", "policies.txt")

# ---------------------------------------------------------------------------
# Main generate button handler
# ---------------------------------------------------------------------------

def on_generate(event) -> None:
    """Callback fired when the user clicks 'Generate'."""
    global _generated_policies

    btn = document.querySelector("#generate-btn")
    btn.disabled = True
    btn.innerHTML = "Generating…"

    # Show processing indicator
    indicator = document.querySelector("#processing-indicator")
    indicator.classList.remove("hidden")

    # Clear previous results
    preview_div = document.querySelector("#preview-area")
    preview_div.innerHTML = ""
    document.querySelector("#download-section").classList.add("hidden")

    try:
        policies = _generate_policies()
        if policies is None:
            # Error already alerted inside _generate_policies
            return
        _generated_policies = policies
        _update_preview(policies)
        # Enable download buttons
        document.querySelector("#download-section").classList.remove("hidden")
    except Exception as exc:
        tb = traceback.format_exc()
        preview_div.innerHTML = (
            '<p class="text-red-600 font-semibold">An error occurred:</p>'
            f'<pre class="text-xs mt-1 whitespace-pre-wrap">{tb}</pre>'
        )
    finally:
        indicator.classList.add("hidden")
        btn.disabled = False
        btn.innerHTML = "Generate"

# ---------------------------------------------------------------------------
# Wire up DOM events on page load
# ---------------------------------------------------------------------------

def _setup() -> None:
    """Attach event listeners to the interactive UI elements."""
    document.querySelector("#generate-btn").addEventListener("click", create_proxy(on_generate))
    document.querySelector("#download-pdf").addEventListener("click", create_proxy(download_pdf))
    document.querySelector("#download-json").addEventListener("click", create_proxy(download_json))
    document.querySelector("#download-txt").addEventListener("click", create_proxy(download_txt))

# Call setup now; PyScript ensures the DOM is ready before executing this code.
_setup()
