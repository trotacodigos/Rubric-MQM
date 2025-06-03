import argparse
import json
import logging
import warnings
from typing import Union

import pandas as pd

from evaluator.call_api import get_api
import evaluator.promptcue as cue
from evaluator import worker as rubric_worker

logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore")


# === Slot Scenario Selection ===
def select_scenario(name: str):
    match name:
        case "deepcat":
            from evaluator.slot_scenarios.deepcat import Prompt
        case "deepshot":
            from evaluator.slot_scenarios.deepshot import Prompt
        case "deepcatshot":
            from evaluator.slot_scenarios.deepcatshot import Prompt
        case "deeprubric":
            from evaluator.slot_scenarios.deeprubric import Prompt
        case "deepsqm":
            from evaluator.slot_scenarios.deepsqm import Prompt
        case _:
            from evaluator.slot_scenarios.gemba import DefaultPrompt as Prompt
    return Prompt


def select_parser(name: str):
    if name in ('deeprubric', 'deepsqm'):
        from parser.scale_parser import parse_annotations
    else:
        from parser.no_scale_parser import parse_annotations
    return parse_annotations


# === Request Preparation ===
def prepare_api_requests(cfg: dict, df: pd.DataFrame) -> pd.DataFrame:
    prompt_cls = select_scenario(cfg.get("slot", "gemba"))
    scale = cfg["scale"] if cfg["slot"] in ('deeprubric', 'deepsqm') else None

    def create_prompt(row):
        obj = prompt_cls(
            source_lang=row.source_lang,
            target_lang=row.target_lang,
            source_seg=row.source,
            target_seg=row.target,
            reference_seg=row.reference if cfg['with_ref'] else None,
            scale=scale,
        )
        obj.with_ref = cfg['with_ref']
        messages = obj.generate_message()

        if cfg['promptcue']:
            obj.template_obj = cue.create_cue(obj.template_obj)

        messages = obj.generate_message()
        if not cfg['promptcue']:
            messages = cue.remove_tag_from_content(messages)

        return {
            'id': row.id,
            'request': {
                'model': cfg.get('model', 'gpt-3.5-turbo'),
                'messages': messages,
            },
            'temperature': cfg.get('temperature', 0),
            'max_tokens': cfg.get('max_tokens', 1024)
        }

    df['prompt'] = df.apply(create_prompt, axis=1)
    return df


# === Review Execution ===
def process_and_review_batch(data: Union[str, pd.DataFrame],
                             output_file: str,
                             error_log: str,
                             cfg: dict):

    df = pd.read_csv(data) if isinstance(data, str) else data
    df = prepare_api_requests(cfg, df)
    responses = get_api(cfg['key'], df.prompt.tolist())

    if len(df) != len(responses):
        logging.error("Mismatch between prompts and responses. Saving error log.")
        with open(error_log, 'w') as f:
            for line in responses:
                f.write(json.dumps(line) + '\n')
        raise ValueError("Prompt-response count mismatch.")

    df["reviews"] = [res['content'] for res in responses]
    df["total_token"] = [res['usage'] for res in responses]

    try:
        parse_fn = select_parser(cfg['slot'])
        parse_fn(df).to_csv(output_file, index=False)
    except Exception as e:
        logging.warning(f"Parsing failed: {e}. Saving raw output.")
        df[["id", "reviews", "total_token"]].to_csv(output_file, index=False)

    logging.info(f"Saved processed results to {output_file}")


# === CLI Parser ===
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input-file', required=True)
    parser.add_argument('-o', '--output-file', required=True)
    parser.add_argument('-e', '--error-log', required=True)
    parser.add_argument('-m', '--model-name', default='gpt-4.1-mini')
    parser.add_argument('-t', '--temperature', type=float, default=0.0)
    parser.add_argument('-x', '--max-tokens', type=int, default=1024)
    parser.add_argument('-b', '--batch-mode', action='store_true')
    parser.add_argument('-w', '--with-ref', action='store_true')
    parser.add_argument('-p', '--promptcue', action='store_true')
    parser.add_argument('-s', '--slot', default='gemba')
    parser.add_argument('-c', '--scale', type=int, default=0)
    return parser.parse_args()


# === Entry Point ===
if __name__ == "__main__":
    args = parse_args()

    if args.slot in ('deeprubric', 'deepsqm') and args.scale not in (4, 8, 100):
        raise ValueError("Invalid scale value for the selected slot.")

    reviewer_cfg = {
        'model': args.model_name,
        'temperature': args.temperature,
        'max_tokens': args.max_tokens,
        'with_ref': args.with_ref,
        'key': [],  # 🔒 Replace with actual key
        'promptcue': args.promptcue,
        'scale': args.scale,
        'slot': args.slot,
    }

    df = pd.read_csv(args.input_file)
    rubric_worker.main(df, args.output_file, args.error_log, reviewer_cfg, args.batch_mode, process_and_review_batch)