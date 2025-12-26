# run.py
import argparse
import pandas as pd
import yaml

from metric.modules.ape import run_batch


def main():
    parser = argparse.ArgumentParser(
        description="Posteditor metric runner"
    )
    parser.add_argument("--input", required=True, help="Input CSV")
    parser.add_argument("--output", required=True, help="Output file (csv/jsonl)")
    parser.add_argument("--config", default="metric/config/default.yaml")
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    df = pd.read_csv(args.input)

    run_batch(
        df=df,
        cfg=cfg,
        workers=args.workers,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()