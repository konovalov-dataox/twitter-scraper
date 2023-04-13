import importlib.util
import subprocess
import sys


def is_installed(package_name):
    spec = importlib.util.find_spec(package_name)
    return bool(spec)


def setup(requirements):
    for package in requirements:
        if not is_installed(package):
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
