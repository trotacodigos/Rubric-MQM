import json
import re

from metric.utils.utils import preserve_paragraph_structure


def sanitize_response(raw_response):
    cleaned = raw_response
    cleaned = re.sub(r'(".*?")\s*\(', r'\1 (', cleaned)
    cleaned = re.sub(r'(\"\s*\))\s*or\s*', r'\1, or ', cleaned)
    cleaned = re.sub(r'(\"\s*\))\s*but\s*', r'\1, but ', cleaned)
    return cleaned


def clean_suggestion(raw_suggestion):
    quote_match = re.search(r"'([^']+)'|\"([^\"]+)\"", raw_suggestion)
    if quote_match:
        return quote_match.group(1) or quote_match.group(2)
    fallback = raw_suggestion.split('(')[0].split('or')[0].split('but')[0].strip()
    return fallback


def parse_response(response, tgt_text):
    """
    Parses postedit task response into unified dictionary structure.
    """
    raw = response.get("content", "")
    usage = response.get("usage", 0)

    corrected = tgt_text  # fallback
    details = []
    MIN_SAFE_SPAN_LEN = 2

    try:
        safe_response = sanitize_response(raw)
        parsed = json.loads(safe_response)

        if isinstance(parsed, dict):
            for span, info in parsed.items():
                if not isinstance(info, dict):
                    continue

                suggestion = clean_suggestion(info.get("suggestion", "").strip())
                if span.lower() == "no-error" or not suggestion or suggestion == span:
                    continue

                if len(span) < MIN_SAFE_SPAN_LEN:
                    continue

                # When replacing, try two steps:
                # 1) When the matched span is surrounded by spaces
                pattern_space = rf' {re.escape(span)} '
                corrected, count = re.subn(pattern_space, f' {suggestion} ', corrected, count=1)

                # 2) When the matched span is attached without spaces
                if count == 0:
                    pattern_general = re.escape(span)
                    corrected, _ = re.subn(pattern_general, suggestion, corrected, count=1)

                category = (
                    info.get("category")
                    or info.get("error_category")
                    or info.get("error category")
                    or "unspecified"
                )

                info_clean = {
                    "span": span,
                    "suggestion": suggestion,
                    "category": category,
                    "severity": info.get("severity", 0)
                }
                details.append(info_clean)

    except Exception:
        corrected = tgt_text

    corrected = preserve_paragraph_structure(tgt_text, corrected)

    return {
        "success": True,
        "data": {"text": corrected, "tokens": usage},
        "details": details,
        "error": None
    }
