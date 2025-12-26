import copy
import logging
import os
import random
import time
from typing import Dict, Any, List, Optional

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

logging.basicConfig(level=logging.WARNING)


def _load_api_keys() -> List[str]:
    """
    Load OpenAI API keys from environment variables.
    Priority:
      1) OPENAI_API_KEYS (comma-separated)
      2) OPENAI_API_KEY (single)
    """
    keys = os.getenv("OPENAI_API_KEYS")
    if keys:
        parsed = [k.strip() for k in keys.split(",") if k.strip()]
        if parsed:
            return parsed

    key = os.getenv("OPENAI_API_KEY")
    if key:
        return [key.strip()]

    raise RuntimeError(
        "No OpenAI API key found. "
        "Set OPENAI_API_KEY or OPENAI_API_KEYS."
    )


def _select_api_key(api_keys: List[str]) -> str:
    return random.choice(api_keys)

def _get_client() -> OpenAI:
    api_keys = _load_api_keys()
    api_key = _select_api_key(api_keys)
    return OpenAI(api_key=api_key)


@retry(
    wait=wait_random_exponential(min=1, max=60),
    stop=stop_after_attempt(6),
    reraise=True,
)
def _completion(client: OpenAI, **kwargs) -> Any:
    return client.chat.completions.create(**kwargs)


def call_api(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        raw = _completion(_get_client(), **request["request"])
        return _verify_response(raw)
    except Exception as e:
        logging.warning(f"API call failed: {e}")
        return {"content": None, "usage": 0}


def _verify_response(response: Any) -> Dict[str, Any]:
    if not hasattr(response, "choices") or not response.choices:
        logging.warning(f"Malformed response: {response}")
        return {"content": None, "usage": 0}

    choice = response.choices[0]
    content = getattr(choice.message, "content", None)

    if content and choice.finish_reason == "stop":
        usage = getattr(getattr(response, "usage", None), "total_tokens", 0)
        return {
            "content": content.strip(),
            "usage": usage,
        }

    logging.warning(f"Incomplete response: {response}")
    return {"content": None, "usage": 0}


def call_with_semantic_retry(
    request: Dict[str, Any],
    *,
    max_retries: int = 2,
) -> Dict[str, Any]:
    current = copy.deepcopy(request)

    for attempt in range(max_retries + 1):
        result = call_api(current)

        if result["content"]:
            return result

        # semantic fallback
        if result["content"] is None:
            current["temperature"] += 1
            logging.warning(
                f"[Retry {attempt+1}] Increase temperature → {current['temperature']}"
            )
        else:
            current["max_tokens"] += 200
            logging.warning(
                f"[Retry {attempt+1}] Increase max_tokens → {current['max_tokens']}"
            )

    return result


def get_one_api(request: dict):
    return call_with_semantic_retry(request)


def get_api(
    requests: List[Dict[str, Any]],
    *,
    sleep_sec: Optional[float] = None,
) -> List[Dict[str, Any]]:
    api_keys = _load_api_keys()

    responses = []

    for idx, request in enumerate(requests):
        api_key = api_keys[idx % len(api_keys)]
        result = call_with_semantic_retry(api_key, request)
        responses.append(result)

        if sleep_sec:
            time.sleep(sleep_sec)

    return responses