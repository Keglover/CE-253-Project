import sys
import subprocess
import argparse

from pathlib import Path

def bipia_setup():
    parser = argparse.ArgumentParser(description="Provide the file path to your BIPIA repo clone")

    parser.add_argument("bipia_dir", type=Path, help="Provide the path to the BIPIA repo clone")
    bipia_path = parser.parse_args()

    if not bipia_path.exists():
        print(f"ERROR: The path provided ({bipia_path}) is not valid, and could not be found. Make sure to clone the BIPIA repo (link in the README) before running this script.\n")
        return -1

    try:
        print("INFO: Checking if bipia is installed")
        subprocess.run([sys.executable, "-m", "pip", "show", "bipia"], check=True)
        print("SUCCESS: Found a valid bipia install, project should be able to run correctly")
        return
    
    except subprocess.CalledProcessError:
        print(f"INFO: Could not find bipia install, proceeding to install")
    
    finally:
        print("INFO: Installing BIPIA as a Python module using provided path")

        try:
            subprocess.run([sys.executable, "-m", "pip", "install", bipia_path.bipia_dir], check=True)
            print("SUCCESS: BIPIA should now be installed in your environment and able to be used for the project.\n")

        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install bipia, returning error {e}. Please make sure you have cloned the repo and that you put the path to the repo file.\n")


if __name__ == "__main__":
    bipia_setup()