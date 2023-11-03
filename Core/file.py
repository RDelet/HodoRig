import json
import os
import traceback

from HodoRig.Core.logger import log


def build_directory(path: str):
    dir, file = os.path.split(path)
    path = dir if '.' in file else path

    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Error on build path {path}")


def dump_json(data, path: str):
    try:
        build_directory(path)
        data_str = json.dumps(data)
        with open(path, "w") as handle:
            handle.write(data_str)
    except:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Impossible to write json {path} !")


def read_json(path: str):
    if not os.path.isfile(path):
        raise RuntimeError(f"Path {path} is not a file !")

    try:
        with open(path, "r") as handle:
            return json.load(handle)
    except Exception:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Error on read file {path}")
