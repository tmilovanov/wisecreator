import os
import sys
import stat
import shutil
import platform
import subprocess
from pathlib import Path

def run_process(args, cwd=None, wait=True):
    str_args = list(map(str, args))
    if wait:
        return subprocess.run(str_args, cwd=cwd, capture_output=True)
    else:
        return subprocess.Popen(str_args, cwd=cwd)

def prepare_empty_folder(folder_path):
    folder_path = Path(folder_path)
    if folder_path.exists():
        shutil.rmtree(folder_path)
    os.mkdir(folder_path)

def get_resource_path(rsrc_relative_path):
    if getattr(sys, 'frozen', False): # Running as compiled with pyinstaller
        # sys._MEIPASS exists only when application is running as compiled with pyinstaller application
        # pylint comment is added, to disable IDE warning on the next line
        base_path = sys._MEIPASS # pylint: disable=no-member
    else:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, rsrc_relative_path)


def get_path_to_data(data_name):
    return os.path.join(get_resource_path("data"), data_name)


def get_path_to_mobitool():
    path_to_third_party = get_resource_path("third_party")

    path_to_mobitool = ""
    if platform.system() == "Linux":
        if sys.maxsize > 2**32:
            path_to_mobitool = os.path.join(path_to_third_party, "mobitool-linux-x86_64")
        else:
            path_to_mobitool = os.path.join(path_to_third_party, "mobitool-linux-i386")
    if platform.system() == "Windows":
        path_to_mobitool = os.path.join(path_to_third_party, "mobitool-win32.exe")
    if platform.system() == "Darwin":
        path_to_mobitool = os.path.join(path_to_third_party, "mobitool-osx-x86_64")

    # add executed permission
    current_permission = os.stat(path_to_mobitool)
    os.chmod(path_to_mobitool, current_permission.st_mode | stat.S_IEXEC)
    return path_to_mobitool


def get_path_to_kindle_unpack() -> Path:
    p = "third_party"
    p = os.path.join(p, "KindleUnpack")
    p = os.path.join(p, "lib")
    p = os.path.join(p, "kindleunpack.py")
    return Path(get_resource_path(p))


def get_path_to_py_interpreter() -> Path:
    return Path(sys.executable)

def block_print():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enable_print():
    sys.stdout = sys.__stdout__