from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analyze_pricing import run_analysis
from src.generate_data import save_data


def main():
    data_path = ROOT / "data" / "synthetic_merchants.csv"
    save_data(data_path)
    _, summary, _ = run_analysis(data_path, ROOT / "outputs")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

