from __future__ import annotations

from importlib.machinery import SourceFileLoader
from pathlib import Path
import traceback

from ..Core.logger import log
from ..Core import file


_scripts_path = []
_scripts = {}


def __load_module(file_path: str | Path):
    file_name = Path(file_path).with_suffix("").name
    if file_name in _scripts:
        return

    try:
        mod = SourceFileLoader(file_name, str(file_path)).load_module()
        if 'main' not in mod.__dict__:
            log.debug(f"No main function found in {file_path}.")
            return
        _scripts[file_name] = mod
        log.debug(f"QuickScripts {file_name} added.")
    except Exception as e:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"File \"{file_path}\" is not conform !") from e


def register_path(path: str | Path):
    if path in _scripts_path:
        log.warning(f"Path {path} already registered")
        return
    _scripts_path.append(Path(path))


def find_module(script_name: str):
    if script_name in _scripts:
        return _scripts[script_name]


def get_scripts() -> dict:
    return _scripts


def retrieve():
    _scripts.clear()
    for path in _scripts_path:
        for f in file.get_directory_files(path, extension="*.py"):
            if not f.name.startswith("__"):
                __load_module(f)

            