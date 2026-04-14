from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.db.session import SessionLocal
from app.services.etl.importer import stage_csv


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage legacy Chrome Hearts pricing sheet rows.")
    parser.add_argument("csv_path", type=Path, help="Path to the legacy CSV export.")
    parser.add_argument(
        "--source-name",
        default="legacy_csv",
        help="Source name to stamp on staged rows.",
    )
    args = parser.parse_args()

    with SessionLocal() as db:
        count = stage_csv(args.csv_path, db, source_name=args.source_name)
        db.commit()
        print(f"Staged {count} legacy import rows from {args.csv_path}")


if __name__ == "__main__":
    main()
