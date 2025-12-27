import json
from pathlib import Path
from typing import Optional, List, Dict


def gen_message(*, src_lang, tgt_lang, src_text, target, domain, ref_text=None):
    """
    Generates message prompts for post-editing task.
    """
    messages = [
        {"role": "system", "content": "You are a professional evaluator of machine translation quality."}
    ]

    shots = icl_examples()
    messages.extend(shots)

    prompt = create_template(
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        src_text=src_text,
        target=target,
        domain=domain,
        ref_text=ref_text
    )
    messages.append({"role": "user", "content": prompt})

    return messages



def icl_examples() -> List[Dict[str, str]]:
    path = Path(__file__).parent / "icl_examples.jsonl"

    with open(path, "r", encoding="utf-8") as f:
        records = [
            json.loads(line)
            for line in f
            if line.strip()
        ]

    messages: List[Dict[str, str]] = []

    for data in records:
        user_content = create_template(
            src_lang=data["src_lang"],
            tgt_lang=data["tgt_lang"],
            src_text=data["src_text"],
            target=data["target"],
        )

        assistant_content = json.dumps(
            data["answer"],
            ensure_ascii=False,
            indent=2,
        )

        messages.append({
            "role": "user",
            "content": user_content,
        })
        messages.append({
            "role": "assistant",
            "content": assistant_content,
        })

    return messages


def load_instruction(
    *,
    version: str,
    with_ref: bool,
) -> str:
    with open(Path(__file__).parent / "template.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            record = json.loads(line)
            if (
                record.get("version") == version
                and record.get("with_ref") is with_ref
            ):
                return record["instruction"]

    raise ValueError(
        f"No instruction found for version={version}, with_ref={with_ref}"
    )


def create_template(
    *,
    src_lang: str,
    tgt_lang: str,
    src_text: str,
    target: str,
    domain: str | None = None,
    ref_text: str | None = None,
    version: str = "2.0",
) -> str:
    with_ref = ref_text is not None

    instruction = load_instruction(version=version, with_ref=with_ref)
    if domain is not None:
        instruction = instruction.format(domain=domain)

    segments = [
        f"{src_lang} source:\n```{src_text}```",
        f"{tgt_lang} translation:\n```{target}```",
    ]

    if ref_text is not None:
        segments.append(
            f"{tgt_lang} reference:\n```{ref_text}```"
        )

    return "\n\n".join(segments) + "\n\n" + instruction
    
    
    