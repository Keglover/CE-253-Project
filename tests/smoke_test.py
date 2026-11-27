import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "src" / "data" / "bipia_datasets"
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.normalizer import jsonl_to_experiment_cases

cases = jsonl_to_experiment_cases(DATASET_DIR / "email" / "test.jsonl")

assert cases
assert cases[0].case_id
assert cases[0].task
assert cases[0].context
assert cases[0].question
assert cases[0].attack
assert cases[0].attack_id
assert cases[0].expected_answer