'''
Taken from the README on the GitHub page for the
BIPIA public repository.
'''

from bipia import AutoAPIBuilder
from pathlib import Path
from datasets import Dataset

dataset_names = ["email", "code", "qa", "abstract", "table"]
context_data_file = ""
attack_data_file = ""
output_path = ""

not_finished_yet = True

def builder(dataset_name: str, seed=2023) -> Any:
    builder = AutoAPIBuilder.from_name(dataset_name)(seed)
    samples = builder(
        context_data_file,
        attack_data_file,
        enable_stealth=False,
    )

    return Dataset.from_pandas(samples)

def main() -> None:
    if not_finished_yet:
        print("This script has not been implemented yet and will explode if ran. Let's just abort for now instead of doing something we'll regret")
        exit(-4)

    datasets = dict.fromkeys(dataset_names)
    
    for name in dataset_names:
        datasets[name] = builder(name)

    

    pass

main()