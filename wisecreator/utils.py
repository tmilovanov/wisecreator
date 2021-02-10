import os
import shutil
import subprocess
from pathlib import Path

def run_process(args, cwd=None, wait=True):
    str_args = list(map(str, args))
    if wait:
        return subprocess.run(str_args, cwd=cwd, capture_output=True)
    else:
        str_args = list(map(str, args))
        return subprocess.Popen(str_args, cwd=cwd)

def prepare_empty_folder(folder_path):
    folder_path = Path(folder_path)
    if folder_path.exists():
        shutil.rmtree(folder_path)
    os.mkdir(folder_path)