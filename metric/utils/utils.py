import json

def preserve_paragraph_structure(src_text, tgt_text):
    """
    Reconstructs tgt_text to preserve paragraph and line break structure of src_text.
    Supports '\n' (line breaks) and '\n\n' (paragraph breaks).
    """
    tgt_text = tgt_text.strip("```").strip()
    source_parts = src_text.split("\n\n")
    separators = []

    for part in source_parts:
        lines = part.split("\n")
        separators.extend(["\n"] * (len(lines) - 1))
        separators.append("\n\n")

    target_flat = [line for para in tgt_text.split("\n\n") for line in para.split("\n")]

    rebuilt = ""
    for sep, line in zip(separators, target_flat):
        rebuilt += line + sep

    return rebuilt.strip()
