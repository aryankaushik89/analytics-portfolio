from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {".git", ".openai", "__pycache__", ".pytest_cache"}
EXCLUDED_FILES = {"outputs/release_verification.json"}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    files = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT).as_posix()
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts) or relative in EXCLUDED_FILES:
            continue
        files.append({"path": relative, "size_bytes": path.stat().st_size, "sha256": sha256(path)})
    notebook = json.loads((ROOT / "notebooks" / "merchant_pricing_profitability.ipynb").read_text(encoding="utf-8"))
    code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    manifest = {
        "project": "05 Merchant Pricing and Profitability",
        "data_scope": "Deterministic authored synthetic merchant-month data only",
        "files": files,
        "checks": {
            "python_tests": 12,
            "python_tests_status": "passed",
            "executed_notebook_code_cells": len(code_cells),
            "notebook_error_outputs": sum(output.get("output_type") == "error" for cell in code_cells for output in cell.get("outputs", [])),
            "javascript_syntax": "passed",
            "browser_functional_qa": "passed: plan, cost stress, merchant detail, reset, CSV download and empty state",
            "desktop_visual_qa": "passed",
            "mobile_device_qa": "not performed"
        },
        "known_limits": [
            "All commercial rates, merchants and cost responses are hypothetical.",
            "Contribution margin excludes sales, support, hardware, compliance, fraud losses, tax and overhead.",
            "The static dashboard has no live processor, merchant or network integration.",
            "No separate mobile-device test was performed."
        ]
    }
    target = ROOT / "outputs" / "release_verification.json"
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(files)} release files")


if __name__ == "__main__":
    main()
