'''
Taken from the README on the GitHub page for the
BIPIA public repository.
'''

from bipia.data import AutoPIABuilder
from pathlib import Path
from datasets import Dataset
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "src" / "data"
OUTPUT_DIR = PROJECT_ROOT / "src" / "results" / "bipia" / "datasets"

DATASET_NAMES = ["email", "code", "qa", "abstract", "table"]
SPLIT = "test"
SEED = 2023

def find_paths(dataset_name: str, split: str)->tuple[Path, Path]:
    context_data_file = DATA_DIR / "benign" / dataset_name / f"{split}.jsonl"

    if dataset_name == "code":
        attack_filename = f"code_attack_{split}.json"
    else:
        attack_filename = f"text_attack_{split}.json"

    attack_data_file = DATA_DIR / "attacks" / "bipia" / attack_filename

    return context_data_file, attack_data_file

def builder(dataset_name:str, split:str = SPLIT, seed:int = SEED) -> Any:
    context_data_file, attack_data_file = find_paths(dataset_name, split)

    if not context_data_file.exists():
        raise FileNotFoundError(f"Context file not found: {context_data_file}")
    if not attack_data_file.exists():
        raise FileNotFoundError(f"Attack file not found : {attack_data_file}")

    builder_class = AutoPIABuilder.from_name(dataset_name)
    pia_builder = builder_class(seed=seed)
    samples = pia_builder(str(context_data_file), str(attack_data_file), enable_stealth=False,)

    return Dataset.from_pandas(samples, preserve_index=False)

def save_dataset(set_name:str, split:str = SPLIT,) -> Path:
    dataset = builder(dataset_name=set_name, split=split)

    output_dir = OUTPUT_DIR / set_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{split}.jsonl"
    dataset.to_json(str(output_path))

    print(f"Saved {set_name}/{split} to {output_path}")
    print(f"Rows: {len(dataset)}")

    return output_path

def main() -> None:
    for dataset_name in DATASET_NAMES:
        save_dataset(dataset_name)

if __name__ == "__main__":
    main()