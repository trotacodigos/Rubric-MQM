import csv
import json
import random
from multiprocessing import Pool, cpu_count
from typing import Dict, Any, Optional

import pandas as pd
from tqdm import tqdm

from metric.core.call_api import get_one_api
from metric.prompt.fewshot import gen_message
from metric.parser.parse import parse_response


REQUIRED_COLS = ("src_lang", "tgt_lang", "src_text", "target")


def build_request(
    *,
    src_lang: str,
    tgt_lang: str,
    src_text: str,
    target: str,
    domain: str,
    model: str,
    temperature: float,
    max_tokens: int,
    ref_text: Optional[str] = None,
) -> Dict[str, Any]:
    messages = gen_message(
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        src_text=src_text,
        target=target,
        ref_text=ref_text,
        domain=domain,
    )

    return {
        "request": {
            "model": model,
            "messages": messages,
        },
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def run_single(
    cfg: Dict[str, Any],
    row: Dict[str, Any],
):
    request = build_request(
        src_lang=row["src_lang"],
        tgt_lang=row["tgt_lang"],
        src_text=row["src_text"],
        target=row["target"],
        ref_text=row.get("ref_text"),
        domain=row.get("domain", None),
        model=cfg["model"]["name"],
        temperature=cfg["model"]["temperature"],
        max_tokens=cfg["model"]["max_tokens"],
    )

    response = get_one_api(request)
    return parse_response(response, row["target"])


def run_batch(
    df: pd.DataFrame,
    cfg: Dict[str, Any],
    workers: Optional[int] = None,
    output_path: Optional[str] = None,
    progress_callback=None,
):
    def _process_row(args):
        row, cfg = args
        return run_single(cfg, row)

    if not all(col in df.columns for col in REQUIRED_COLS):
        raise ValueError(f"Missing required columns: {REQUIRED_COLS}")

    workers = workers or cpu_count()
    is_jsonl = output_path and output_path.endswith(".jsonl")

    task_data = [
        (row.to_dict(), cfg)
        for _, row in df.iterrows()
    ]

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="" if not is_jsonl else None,
    ) as f, Pool(processes=workers) as pool:

        writer = None

        for idx, result in enumerate(
            tqdm(
                pool.imap(_process_row, task_data),
                total=len(task_data),
                ncols=100,
                colour="cyan",
            )
        ):
            if is_jsonl:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
            else:
                if writer is None:
                    writer = csv.DictWriter(f, fieldnames=result.keys())
                    writer.writeheader()
                writer.writerow(result)

            if progress_callback:
                progress_callback(idx)