import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "src" / "data" / "bipia_datasets"
sys.path.insert(0, str(PROJECT_ROOT))

#from prompting import prompt_schema
from src.prompting import prompt_builder
from src.data.normalizer import jsonl_to_experiment_cases, NormalizedCase

cases = jsonl_to_experiment_cases(DATASET_DIR / "email" / "test.jsonl")
test_case = cases[0]

print(hasattr(test_case, "example"))
print(isinstance(test_case, NormalizedCase))
prompt = prompt_builder.build_prompt(case=test_case, defense=prompt_builder.DefenseVariant.COMBINED)