import sys
import subprocess
import argparse

from pathlib import Path

def run_pip(*args: str) ->subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "pip" *args], check=True,)

def bipia_setup() -> int:
    parser = argparse.ArgumentParser(description="Provide the file path to your BIPIA repo clone")

    parser.add_argument("bipia_dir", type=Path, help="Provide the path to the BIPIA repo clone. If you have not cloned the repo from https://github.com/microsoft/BIPIA/tree/main then stop this, do that, and come back.")
    parser.add_argument("--non-editable", action="store_true", help="Perform a regular installation rather than an installable installation. If you don't know what this means, check the README.")
    args = parser.parse_args()

    bipia_path = args.bipia_dir.expanduser().resolve()

    if not bipia_path.exists():
        print(f"ERROR: The path provided ({bipia_path}) is not valid, and could not be found. Make sure to clone the BIPIA repo (link in the README) before running this script.\n", file=sys.stderr)
        return -1

    if not bipia_path.is_dir():
        print(f"ERROR: The path provided ({bipia_path}) is not a valid directory.\n", file=sys.stderr)
        return -1

    packaging_files = (bipia_path / "pyproject.toml",
                       bipia_path / "setup.py",
                       bipia_path /  "setup.cfg")

    if not any(path.exists() for path in packaging_files):
        print(f"ERROR: The provided directory was found, but is not installable as a Python project. This requires one of pyproject.toml, setup.py, or setup.cfg - none of these were found.\n", file=sys.stderr)
        return -1

    print(f"INFO: Repository of path {bipia_path}")

    try:
        run_pip("show", "bipia")
        print("INFO: BIPIA has already been installed on this system. Exiting.\n")
        return 1
    except subprocess.CalledProcessError:
        print("INFO: BIPIA has not been installed. Proceeding to install proceedure.\n")

    install_target = str(bipia_path)

    if not args.non_editable:
        install_target = f"{install_target}"

        print("INFO: Installing BIPIA in editable mode....")
        install_args = ["install", "--editable", install_target]
    else:
        print("INFO: Installing BIPIA....")
        install_args = ["install", install_target]

    try:
        run_pip(*install_args)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: BIPIA installation failed: {e}", file=sys.stderr)
        return -1

    try:
        run_pip("show", "bipia")
    except subprocess.CalledProcessError:
        print("WARNING: Installation completed, but pip cannot find the BIPIA package", file=sys.stderr)
        return -1

    print("SUCCESS: BIPIA has been installedd and available to run within the current Python environment")
    return 0
          
if __name__ == "__main__":
    setup_code = bipia_setup()

    if setup_code == -1:
        print("An error occurred when attempting to install BIPIA.")
    elif setup_code == 0:
        print("BIPIA was successfully installed in the current environment.")
    elif setup_code == 1:
        print("BIPIA is already installed on the Python environment.")
    else:
        print("I don't know what you did, but this was not supposed to happen....")
        exit(-1)