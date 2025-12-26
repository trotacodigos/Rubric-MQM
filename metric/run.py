import argparse
import pandas as pd
import yaml

from metric.modules.ape import postedit
from metric.modules.judge import evaluate


def main():
    parser = argparse.ArgumentParser(
        description="Rubric-MQM runner (APE / LLM-as-Judge)"
    )
    parser.add_argument(
        "--mode",
        choices=["ape", "judge"],
        required=True,
        help="Run mode: automatic post-editing (ape) or LLM-as-judge (judge)",
    )
    parser.add_argument("--input", required=True, help="Input CSV")
    parser.add_argument("--output", required=True, help="Output file (csv/jsonl)")
    parser.add_argument("--config", default="metric/config/default.yaml")
    parser.add_argument("--workers", type=int, default=2)

    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    df = pd.read_csv(args.input)

    if args.mode == "ape":
        postedit(
            df=df,
            cfg=cfg,
            workers=args.workers,
            output_path=args.output,
        )
    else:  # judge
        evaluate(
            df=df,
            cfg=cfg,
            workers=args.workers,
            output_path=args.output,
        )


if __name__ == "__main__":
    main()