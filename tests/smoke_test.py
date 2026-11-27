import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "src" / "data" / "bipia_datasets"
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.normalizer import jsonl_to_experiment_cases

# Experiment Cases

cases = jsonl_to_experiment_cases(DATASET_DIR / "email" / "test.jsonl")

assert cases is not None
assert cases[0].case_id
assert cases[0].task
assert cases[0].context
assert cases[0].question
assert cases[0].attack
assert cases[0].attack_id
assert cases[0].expected_answer

# Adapters
from src.model_adapters import base, ollama

adapter_ol = ollama.OllamaAdapter("qwen2.5:7b")

response = adapter_ol.generate_from_prompt("Respond with exactly: Ollama connection successful")

assert response is not None             # If it's None, something is wrong
assert response.content == "Ollama connection successful"
assert response.tool_calls is not None  # We don't necessarily expect tool calls right now, just want to make sure it isn't None
assert response.model == "qwen2.5:7b"