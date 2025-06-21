import pandas as pd
import numpy as np
import re
from typing import List, Dict

META_CAT = {
    'untranslated': 'accuracy', 
    'mistranslation': 'accuracy',
    'addition': 'accuracy',
    'word order': 'word order',
    'terminology': 'terminology'
}


def parse_one(text: str) -> dict:
    """
    Parses a single line of MQM annotation.
    Format: "span" - category - severity

    Returns:
        dict: {span, category, severity} or empty dict if invalid
    """
    match = re.search(r'"(.*?)"\s*-\s*(\w+)\s*-\s*(\d+)', text)
    if not match:
        return {}
    span, category, severity = match.groups()
    return {
        'span': span,
        'category': category,
        'severity': int(severity)
    }


def parse_many(review: str) -> List[Dict[str, str]]:
    """
    Parses all valid annotations from a review string.
    """
    return [res for line in review.splitlines() if (res := parse_one(line))]


def _has_no_error(cats: List[str]) -> bool:
    return any(c in ['no-error', 'no error'] for c in cats)


def _score_from_items(items: List[Dict[str, str]]) -> float:
    return sum(item['severity'] for item in items) / -100 if items else 0


def parse_annotations(
    source_df: pd.DataFrame, 
    review_df: pd.DataFrame = None, 
    match_gold: bool = False,
) -> pd.DataFrame:
    """
    Parses MQM review annotations into a structured form with predicted categories, severities, and scores.

    Args:
        source_df: Original data with gold spans.
        review_df: DataFrame with 'reviews' column.
        match_gold: If True, only include spans that match gold_span.

    Returns:
        DataFrame with new 'answer' column.
    """
    source_df = source_df.copy()
    if review_df is not None:
        source_df['reviews'] = review_df['reviews']
    answers = []

    for row in source_df.itertuples(index=False):
        review = getattr(row, 'reviews', '')
        gold_span = getattr(row, 'error_span', '')

        parsed = parse_many(review)
        if not parsed or _has_no_error([p['category'] for p in parsed]) or not gold_span:
            answers.append({'cat_pred': [], 'sev_pred': [], 'score': 0})
            continue

        if match_gold:
            parsed = [
                p for p in parsed 
                if gold_span in p['span'] or p['span'] in gold_span
            ]

        result = {
            'cat_pred': [p['category'] for p in parsed],
            'sev_pred': [p['severity'] for p in parsed],
            'score': _score_from_items(parsed)
        }
        answers.append(result)

    source_df['answer'] = answers

    return source_df