from importlib.machinery import SourceFileLoader
import os
import traceback

from HodoRig.Core.logger import log


_scripts_path = []
_scripts = {}


def __load_module(file_path: str):
    _, file = os.path.split(file_path)
    file_name, _ = os.path.splitext(file)
    try:
        mod = SourceFileLoader(file_name, file_path).load_module()
        if 'main' not in mod.__dict__:
            log.debug(f"No main function found in {file_path}.")
            return
        _scripts[mod.kScriptName] = mod
        log.debug(f"QuickScripts {file} added.")
    except Exception:
        log.debug(traceback.format_exc())
        log.debug('File "{0}" is not conform !'.format(file_path))


def register_path(path: str):
    if path in _scripts_path:
        log.warning(f"Path {path} already registered")
        return
    _scripts_path.append(path)


def find_module(script_name: str):
    if script_name in _scripts:
        return _scripts[script_name]


def get_scripts() -> dict:
    return _scripts


def retrieve():
    _scripts.clear()
    for p in _scripts_path:
        for f in os.listdir(p):
            if '__' in f or not f.endswith('.py'):
                continue
            file_path = os.path.normpath(os.path.join(p, f))
            __load_module(file_path)

            