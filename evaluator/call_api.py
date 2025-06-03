import openai
import random
import time
import copy
import logging
from concurrent.futures import ProcessPoolExecutor
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tqdm import tqdm
from typing import List, Dict, Any

logging.basicConfig(level=logging.WARNING)


# === API Dispatcher ===
def get_api(api_keys: List[str], requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    assert api_keys, "Introduce your API keys!"
    params = calc_default_params(len(api_keys))
    responses = []

    with ProcessPoolExecutor(max_workers=params['num_workers']) as executor:
        for idx, request in tqdm(enumerate(requests), total=len(requests), desc="RubricMQM", ncols=100, colour="yellow"):
            api_key = api_keys[idx % len(api_keys)]
            future = executor.submit(call, api_key=api_key, request=request)
            response = verify_response(future)

            if response['content'] is None:
                updated = copy.deepcopy(request)
                updated['temperature'] += 1
                logging.warning(f"Retrying with increased temperature: {updated['temperature']}")
                future = executor.submit(call, api_key=api_key, request=updated)
                response = verify_response(future)

            elif response['content'] == "":
                updated = copy.deepcopy(request)
                updated['max_tokens'] += 200
                logging.warning(f"Retrying with increased max_tokens: {updated['max_tokens']}")
                future = executor.submit(call, api_key=api_key, request=updated)
                response = verify_response(future)

            responses.append(response)
            time.sleep(params['time_btw_request'])

    return responses


# === Response Checker ===
def verify_response(future) -> Dict[str, Any]:
    response = future.result()
    if hasattr(response, 'choices'):
        choice = response.choices[0]
        if choice.message.content and choice.finish_reason == 'stop':
            return {'content': choice.message.content.strip(), 'usage': response.usage.total_tokens}
    logging.warning(f"Invalid response received: {response}")
    return {'content': None, 'usage': None}


# === Parameter Calculator ===
def calc_default_params(num_keys: int) -> Dict[str, Any]:
    reqs_per_min = 60
    avg_response_sec = 5.0
    buffer_factor = 2

    rps = reqs_per_min / 60
    parallel_requests = rps * avg_response_sec
    num_workers = int(parallel_requests * buffer_factor)
    time_btw_request = 1 / (rps * num_keys)

    return {
        "num_workers": num_workers,
        "time_btw_request": time_btw_request,
    }


# === Retryable Completion ===
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6), reraise=True)
def completion_with_backoff(api_key: str, **kwargs) -> Any:
    client = openai.OpenAI(api_key=api_key)
    return client.chat.completions.create(**kwargs)


# === API Call Wrapper ===
def call(api_key: str, request: Dict[str, Any]) -> Any:
    try:
        return completion_with_backoff(api_key, **request['request'])
    except Exception as e:
        logging.warning(f"Request failed: {e}")
        return {}