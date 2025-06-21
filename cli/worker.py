import argparse
import json
import logging
import math
import warnings
from typing import Union, List
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm

from rubric_mqm.prompt import RubricMQMPrompt
from rubric_mqm import promptcue as cue
from rmqm_parser.scale_parser import parse_annotations
from rubric_mqm.call_api import get_api

# === Configuration ===
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore")


# === API Request Preparation ===
def prepare_api_requests(cfg: dict, df: pd.DataFrame) -> pd.DataFrame:
    prompts = []

    for idx, row in df.iterrows():
        obj = RubricMQMPrompt(
            source_lang=row.source_lang,
            target_lang=row.target_lang,
            source_seg=row.source,
            target_seg=row.target,
            reference_seg=row.reference if cfg['with_ref'] else None,
        )
        obj.with_ref = cfg['with_ref']

        if cfg['promptcue']:
            obj.template_obj = cue.create_cue(obj.template_obj)

        messages = obj.generate_message()
        if not cfg['promptcue']:
            messages = cue.remove_tag_from_content(messages)

        prompts.append({
            'id': idx,
            'request': {
                'model': cfg.get('model', 'gpt-3.5-turbo'),
                'messages': messages,
            },
            'temperature': cfg.get('temperature', 0),
            'max_tokens': cfg.get('max_tokens', 1024)
        })

    df['prompt'] = prompts
    return df


# === Batch Iterator ===
def yield_data_batches(df: pd.DataFrame, batch_size: int = 1000):
    total = math.ceil(len(df) / batch_size)
    for start in tqdm(range(0, len(df), batch_size), desc="Batching", ncols=100, colour="blue", total=total):
        yield df.iloc[start:start + batch_size].reset_index(drop=True)


# === Batch Processing ===
def process_and_review_batch(data: Union[pd.DataFrame, str], 
                             output_path: str, 
                             error_log_path: str, 
                             cfg: dict):

    df = pd.read_csv(data) if isinstance(data, str) else data
    df = prepare_api_requests(cfg, df)
    responses = get_api(cfg['key'], df['prompt'].tolist())

    if len(df) != len(responses):
        logging.error("Mismatch between prompts and responses. Writing error log.")
        with open(error_log_path, 'w') as f:
            for res in responses:
                f.write(json.dumps(res) + '\n')
        raise ValueError("Prompt-response count mismatch.")

    df["reviews"] = [res['content'] for res in responses]
    df["total_token"] = [res['usage'] for res in responses]
    df["model"] = cfg["model"]
    df.drop(columns=['prompt'], inplace=True)

    try:
        parse_annotations(df).to_csv(output_path, index=False)
    except Exception as e:
        logging.warning(f"Parsing failed: {e}. Saving fallback output.")
        df[["id", "reviews", "total_token"]].to_csv(output_path, index=False)

    logging.info(f"Saved processed results to {output_path}")
    
    
def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--input-file', required=True, help='Input CSV file path')
    parser.add_argument('-o', '--output-file', required=True, help='Output CSV file path')
    parser.add_argument('-e', '--error-log', required=True, help='Path to save error logs (.jsonl)')
    parser.add_argument('-m', '--model-name', default='gpt-4.1-mini')
    parser.add_argument('-t', '--temperature', type=float, default=0.0)
    parser.add_argument('-x', '--max-tokens', type=int, default=1024)
    parser.add_argument('-b', '--batch-mode', action='store_true')
    parser.add_argument('-w', '--with-ref', action='store_true')
    parser.add_argument('-p', '--promptcue', action='store_true')
    return parser.parse_args()


# === Main Routine ===
def run(df: pd.DataFrame, 
         output_path: str, 
         error_log_path: str, 
         cfg: dict, 
         batch_mode: bool, 
         runner=process_and_review_batch):

    if not batch_mode:
        runner(df, output_path, error_log_path, cfg)
        return

    batch_files: List[str] = []
    for i, batch_df in enumerate(yield_data_batches(df)):
        batch_out_path = f"{output_path.rstrip('.csv')}_{i}.csv"
        runner(batch_df, batch_out_path, error_log_path, cfg)
        batch_files.append(batch_out_path)

    if len(batch_files) > 1:
        try:
            combined_df = pd.concat([pd.read_csv(f) for f in batch_files])
            combined_df.to_csv(output_path, index=False)
            logging.info(f"Combined batch output saved to {output_path}")
        except Exception as e:
            logging.error(f"Failed to combine batch outputs: {e}")
            
            
def main():
    # Load environment variables
    load_dotenv()
    
    keys_raw = os.getenv("OPENAI_API_KEYS")
    if not keys_raw:
        raise ValueError("Missing OPENAI_API_KEYS in .env file!")

    api_keys = [key.strip() for key in keys_raw.split(",") if key.strip()]
    if not api_keys:
        raise ValueError("No valid API keys found in OPENAI_API_KEYS")
        
    args = arg_parse()
    cfg = {
        'model': args.model_name,
        'temperature': args.temperature,
        'max_tokens': args.max_tokens,
        'with_ref': args.with_ref,
        'key': api_keys,
        'promptcue': args.promptcue,
    }
    input_df = pd.read_csv(args.input_file)
    run(input_df, args.output_file, args.error_log, cfg, args.batch_mode)

    
# === CLI Interface ===
if __name__ == "__main__":
    main()

    

    