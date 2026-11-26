'''
Taken from the README on the GitHub page for the
BIPIA public repository.
'''
import subprocess
import sys
import shutil

from bipia.data import AutoPIABuilder
from pathlib import Path
from datasets import Dataset
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "src" / "data"
OUTPUT_DIR = PROJECT_ROOT / "src" / "data" / "bipia_datasets"
BIPIA_BENCHMARK = PROJECT_ROOT / "BIPIA" / "benchmark"
QA_SOURCE_DIR = BIPIA_BENCHMARK / "qa"

DATASET_NAMES = ["email", "code", "table"]
EXT_DATASET_NAMES = ["qa", "abstract"]
SPLIT = "test"
SEED = 2023

def find_paths(dataset_name: str, split: str)->tuple[Path, Path]:
    context_data_file = DATA_DIR / "benign" / dataset_name / f"{split}.jsonl"

    if dataset_name == "code":
        attack_filename = f"code_attack_{split}.json"
    else:
        attack_filename = f"text_attack_{split}.json"

    attack_data_file = DATA_DIR / "attacks" / attack_filename

    return context_data_file, attack_data_file

def builder(dataset_name:str, split:str = SPLIT, seed:int = SEED) -> Any:

    if dataset_name in EXT_DATASET_NAMES:
        pass
        context_data_file = external_builder(dataset_name, split, qa_source_dir=QA_SOURCE_DIR)
        _, attack_data_file = find_paths(dataset_name, split)
    else:
        context_data_file, attack_data_file = find_paths(dataset_name, split)

    if not context_data_file.exists():
        raise FileNotFoundError(f"Context file not found : {context_data_file}")
    if not attack_data_file.exists():
        raise FileNotFoundError(f"Attack file not found : {attack_data_file}")

    builder_class = AutoPIABuilder.from_name(dataset_name)
    pia_builder = builder_class(seed=seed)
    samples = pia_builder(str(context_data_file), str(attack_data_file), enable_stealth=False,)

    return Dataset.from_pandas(samples, preserve_index=False)

def external_builder(dataset_name:str, split: str, qa_source_dir: Path | None = None) -> Path:
    special_datasets = ["qa", "abstract"]

    if dataset_name not in special_datasets:
        raise ValueError(f"Unsupported external dataset: {dataset_name} | Expected one of {special_datasets}")

    if split not in {"train", "test"}:
        raise ValueError(f"Unsupported split: {split} | Expected 'train' or 'test'.")

    spec_dir = BIPIA_BENCHMARK / dataset_name
    process_script_name = spec_dir / "process.py"

    if not process_script_name.exists():
        raise FileNotFoundError(f"BIPIA processing script not forund for {dataset_name}")

    if dataset_name == "qa":

        if qa_source_dir is None:
            raise ValueError("QA dataset preperation requires qa_source_dir to point to the NewsQA source directory in the BIPIA repo")

        qa_source_dir = qa_source_dir.expanduser().resolve()
        
        if not qa_source_dir.exists():
            raise FileNotFoundError(f"NewsQA source directory specified at {qa_source_dir} was not found")

        print(qa_source_dir)

        subprocess.run([sys.executable, str(process_script_name), "--data_dir", str(qa_source_dir)], text=True, check=True, cwd=spec_dir)

    elif dataset_name == "abstract":
        subprocess.run([sys.executable, str(process_script_name)], cwd=spec_dir, check=True, text=True, input="y\n")

    else:
        print("How did you get here? You're not supposed to be here! Enjoy your error, I guess...")
        return None

    source_path = spec_dir / f"{split}.jsonl"

    if not source_path.exists():
            raise FileNotFoundError(f"Dataset preparation completed but expected file was not created: {source_path}")

    dest_dir = DATA_DIR / "benign" / dataset_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / source_path.name 
    shutil.copy2(source_path, dest_path)

    print(f"INFO: Created external context file: {dest_path}")

    return dest_path

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
    for dataset_name in DATASET_NAMES:  # Curently not using external sources because I'm done going down that rabbit hole trying to get them to work. No, I'm not okay, help, PLEASE help :(
        save_dataset(dataset_name)

if __name__ == "__main__":
    main()