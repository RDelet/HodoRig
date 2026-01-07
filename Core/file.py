from __future__ import annotations

import json
import os
import traceback
from pathlib import Path
import subprocess

from ..Core.logger import log
from . import constants


def is_valid_path(path: str | Path) -> bool:
    if isinstance(path, str):
        path = Path(path)
    # Check if path is not empty
    if not str(path).strip():
        return False
    # Check if path have invalid character
    invalid_chars = '<>:"|?*'
    parts = path.parts
    for part in parts:
        if ':' not in part and any(char in part for char in invalid_chars):
            return False
    
    return True


def is_valid_directory(dir_path: str | Path) -> bool:
    return is_valid_path(dir_path) and Path(dir_path).is_dir()


def is_valid_file(file_path: str | Path) -> bool:
    return is_valid_path(file_path) and Path(file_path).is_file()


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
        log.debug(f"File write: {path}")
    except:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Impossible to write json {path} !")


def read_json(path: str):
    if not Path(path).is_file():
        raise RuntimeError(f"Path {path} is not a file !")

    try:
        with open(path, "r") as handle:
            return json.load(handle)
    except Exception:
        log.debug(traceback.format_exc())
        raise RuntimeError(f"Error on read file {path}")


def open_in_ide(path: None | str | Path, line_number: str):
    if not path:
        return
    if isinstance(path, str):
        path = Path(path)

    if not is_valid_file(path):
        log.error(f"Invalid file path: {path}")
        return
        
    if not path.exists():
        log.error(f"File not found: {path}")
        return

    try:
        cmd_string = constants.ide_cmd.format(line_number=line_number, file_path=path)
        subprocess.Popen(cmd_string)
    except Exception as e:
        log.error(f"Error on open file: {e}")


def open_in_explorer(path: None | str | Path):
    if not path:
        return
    if isinstance(path, str):
        path = Path(path)

    if not is_valid_file(path):
        log.error(f"Invalid file path: {path}")
        return
        
    if not path.exists():
        log.error(f"File not found: {path}")
        return

    try:
        path_str = path.as_posix().replace("/", "\\")
        if os.name == 'nt':
            subprocess.Popen(f'explorer /select, {path_str}')
        else:
            os.startfile(path_str)
    except Exception as e:
            log.error(f"Error on open file: {e}")
