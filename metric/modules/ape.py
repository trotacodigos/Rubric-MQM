from metric.core.engine import run_batch

def postedit(**kwargs) -> dict:
    result = run_batch(**kwargs)
    return result["data"]["text"]