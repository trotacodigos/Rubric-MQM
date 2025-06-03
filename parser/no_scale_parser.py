import re
import pandas as pd
from typing import Dict, List, Optional


def parse_one(text: str) -> List[Dict[str, str]]:
    """
    Parses a string of MQM annotations into structured span-category-severity records.

    Args:
        text (str): Multiline MQM annotation text.

    Returns:
        List[Dict]: List of {'span', 'severity', 'category'} dictionaries.
    """
    result = []
    current_severity = None
    valid_severities = {'Critical', 'Major', 'Minor'}

    for line in text.splitlines():
        line = line.strip()
        if line.endswith(':') and line[:-1] in valid_severities:
            current_severity = line[:-1].lower()
        elif line and current_severity:
            match = re.match(r'(.+?)\s*-\s*"(.+?)"', line)
            if match:
                category, span = match.groups()
                result.append({
                    'span': span,
                    'severity': current_severity,
                    'category': category.strip()
                })

    return result


def _calculate_score(parsed_items: List[Dict[str, str]]) -> float:
    """
    Calculate MQM score from parsed items.

    Returns:
        float: Score (capped at -25).
    """
    score_map = {'critical': -25, 'major': -5, 'minor': -1}
    score = 0

    for item in parsed_items:
        cat = item['category'].lower()
        sev = item['severity'].lower()

        if 'punctuation' in cat:
            score += -0.1
        else:
            score += score_map.get(sev, 0)

    return max(score, -25)


def parse_annotations(
    source_df: pd.DataFrame,
    review_df: pd.DataFrame = None,
    match_gold: bool = False
) -> pd.DataFrame:
    """
    Parses reviews and attaches predicted severity/category info + score.

    Args:
        source_df (pd.DataFrame): Original MQM annotations.
        review_df (pd.DataFrame): Model-generated reviews.
        match_gold (bool): If True, only keep predictions matching the gold span.

    Returns:
        pd.DataFrame: source_df with new 'answer' column.
    """
    source_df = source_df.copy()
    if review_df is not None:
        source_df['reviews'] = review_df['reviews']
    parsed_results = []

    for row in source_df.itertuples(index=False):
        review = getattr(row, 'reviews', '')
        gold_span = getattr(row, 'error_span', None)

        parsed = parse_one(review)

        # If matching gold span is required
        if match_gold and gold_span:
            parsed = [
                item for item in parsed
                if gold_span in item['span'] or item['span'] in gold_span
            ]

        if not parsed:
            parsed_results.append({'cat_pred': [], 'sev_pred': [], 'score': 0})
            continue

        result = {
            'cat_pred': [item['category'] for item in parsed],
            'sev_pred': [item['severity'] for item in parsed],
            'score': _calculate_score(parsed) / (-100 if not match_gold else 1)
        }
        parsed_results.append(result)

    source_df['answer'] = parsed_results
    return source_df