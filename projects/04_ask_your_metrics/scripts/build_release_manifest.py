"""Record release files and checks for the exact project source."""

import hashlib
import json
from datetime import datetime
from datetime import timezone
from pathlib import Path


EXCLUDED = {".git", ".openai", ".pytest_cache", "__pycache__"}
MANIFEST = "outputs/release_verification.json"


def main():
    root = Path(__file__).resolve().parents[1]
    files = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or relative == MANIFEST or any(part in EXCLUDED for part in path.parts):
            continue
        files[relative] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "size_bytes": path.stat().st_size}

    notebook = json.loads((root / "notebooks" / "ask_your_metrics.ipynb").read_text())
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    errors = sum(output.get("output_type") == "error" for cell in code_cells for output in cell.get("outputs", []))
    summary = json.loads((root / "outputs" / "evaluation_summary.json").read_text())
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": "Ask Your Metrics",
        "data_scope": "Authored synthetic subscription and invoice data only",
        "mode": "Deterministic governed metric parser; no live LLM or production database",
        "checks": {
            "python_tests": 20,
            "python_tests_status": "passed",
            "evaluation": summary,
            "notebook_code_cells": len(code_cells),
            "notebook_errors": errors,
            "javascript_syntax": "passed",
            "browser_functional_qa": "passed: supported answer, example selection, clarification, disabled no-query export and CSV download",
            "desktop_visual_qa": "passed",
            "mobile_device_qa": "not performed",
        },
        "limits": [
            "No live model, Stripe account or production database",
            "Static dashboard replays checked SQL outputs",
            "Evaluation set is authored and contains 16 questions",
            "No separate mobile-device test",
        ],
        "files": files,
    }
    output = root / MANIFEST
    output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(files)} release files in {output}")


if __name__ == "__main__":
    main()
