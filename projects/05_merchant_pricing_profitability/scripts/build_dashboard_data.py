from pathlib import Path
import json
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analyze_pricing import COST_ASSUMPTIONS
from src.analyze_pricing import PLAN_ASSUMPTIONS

def main():
    merchants = pd.read_csv(ROOT / "data" / "synthetic_merchants.csv")
    records = merchants.to_dict(orient="records")
    payload = {
        "merchants": records,
        "plans": PLAN_ASSUMPTIONS,
        "costs": COST_ASSUMPTIONS,
    }
    content = "window.PRICING_DATA = " + json.dumps(payload, separators=(",", ":")) + ";\n"
    (ROOT / "dist" / "data.js").write_text(content, encoding="utf-8")
    print(f"Saved dashboard data for {len(records)} merchants")


if __name__ == "__main__":
    main()

