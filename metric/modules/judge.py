from metric.core.engine import run_batch

def evaluate(**kwargs) -> dict:
    result = run_batch(**kwargs)
    return result["details"]