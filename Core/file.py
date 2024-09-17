from __future__ import annotations
import json
import os
import traceback
from pathlib import Path
from typing import Optional

from ..Core.logger import log


def is_valid_directory(dir_path) -> bool:
    return Path(dir_path).is_dir()


def is_valid_file(file_path) -> bool:
    return Path(file_path).is_file()


def get_directory_files(dir_path: str | Path, extension: str = "*",
                        recursive: bool = True) -> list:
    dir_path = Path(dir_path)
    if not dir_path.exists():
        raise RuntimeError(f"Path {dir_path} does not exists !")
    if not dir_path.is_dir():
        raise ValueError(f"Invalid directory given: {dir_path}")

    f = dir_path.rglob if recursive else dir_path.glob
    return [x for x in f(extension) if x.is_file()]


def build_directory(path: str | Path):
    if not isinstance(path, Path):
        path = Path(path)
    if path.suffix:
        path = path.with_suffix('')

    try:
        if not path.exists:
            path.mkdir(parents=True, exist_ok=True)
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
