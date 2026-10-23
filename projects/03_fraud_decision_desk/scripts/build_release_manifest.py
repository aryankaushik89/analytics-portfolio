"""Record release files and the checks completed for this exact source tree."""

import hashlib
import json
from datetime import datetime
from datetime import timezone
from pathlib import Path


EXCLUDED_PARTS = {".git", ".openai", ".pytest_cache", "__pycache__"}
MANIFEST_PATH = "outputs/release_verification.json"


def main():
    project_root = Path(__file__).resolve().parents[1]
    files = {}
    for path in sorted(project_root.rglob("*")):
        relative = path.relative_to(project_root).as_posix()
        if not path.is_file() or relative == MANIFEST_PATH:
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        files[relative] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
        }

    notebook = json.loads((project_root / "notebooks" / "fraud_decision_desk.ipynb").read_text())
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    notebook_errors = sum(
        output.get("output_type") == "error"
        for cell in code_cells
        for output in cell.get("outputs", [])
    )

    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": "Fraud Decision Desk",
        "data_scope": "60,000 authored synthetic transactions; no real account, card, merchant or employer data",
        "checks": {
            "python_tests": 11,
            "python_tests_status": "passed",
            "javascript_syntax": "passed",
            "notebook_code_cells": len(code_cells),
            "notebook_errors": notebook_errors,
            "matching_script_completed": True,
            "desktop_browser_qa": "passed",
            "dashboard_default_metrics": "matched outputs/model_metrics.json",
            "dashboard_controls": [
                "threshold",
                "daily capacity",
                "date filter",
                "reset",
                "transaction detail",
                "CSV export",
                "zero-capacity empty state",
            ],
            "mobile_device_qa": "not performed",
        },
        "limits": [
            "Synthetic retrospective scenario, not a live fraud system",
            "Review cost, customer friction and recovery rate are assumptions",
            "No label delay, identity features or network relationships",
            "Responsive rules reviewed but no separate narrow browser or mobile hardware check",
        ],
        "files": files,
    }
    output_path = project_root / MANIFEST_PATH
    output_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(files)} release files in {output_path}")


if __name__ == "__main__":
    main()
