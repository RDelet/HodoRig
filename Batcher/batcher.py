from __future__ import annotations

import argparse
import contextlib
from datetime import datetime
from pathlib import Path
import subprocess


debug_mod = True


# ===========================================
# Create batcher arguments
# ===========================================

parser = argparse.ArgumentParser(description="Maya Batcher", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--name", help="Scenario name")
parser.add_argument("-d", "--directory", help="Batch directory files")
_args = vars(parser.parse_args())


# ===========================================
# Get batcher path
# ===========================================

_current_dir = Path(__file__).parent
_tmp_dir = _current_dir / "TempFiles"
_scenarios_dir = _current_dir / "Scenarios"
_dir_test_files = _current_dir / "TestFiles"
_maya_stand_alone_path = _current_dir / "maya_standAlone.py"

_autodesk_dir = Path(r"C:\Program Files\Autodesk")
_maya_version = "2022"
_maya_dir = _autodesk_dir / f"Maya{_maya_version}"
_mayapy = _maya_dir / "bin" / "mayapy.exe"


# ===========================================
# Init directory
# ===========================================

try:
    if not _tmp_dir.exists():
        _tmp_dir.mkdir(parents=True, exist_ok=True)
        print(f"Directory {_tmp_dir} created !")
except Exception as e:
    raise RuntimeError(f"Impossible to create temp directory") from e


# ===========================================
# subprocess
# ===========================================

def _get_cmd(scene_file: Path, python_file: Path):
    cmd = [str(_mayapy), str(python_file), f"-f \"{str(scene_file)}\""]

    batcher_vars = ["name", "directory"]
    for key, value in _args.items():
        if key not in batcher_vars and value is not None:
            cmd.append(f"--{key} {str(value)}")
    
    return cmd


def run_process(cmd: list | tuple):
    try:
        print(f"subprocess.Popen command: {cmd}")
        proc = subprocess.Popen(cmd,
                                stdin=None,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                bufsize=1,
                                universal_newlines=True,
                                shell=True)
        for line in _unbuffered(proc):
            print(line)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error on excecute command !") from e


def _unbuffered(proc, stream='stdout'):
    stream = getattr(proc, stream)
    with contextlib.closing(stream):
        while True:
            out = []
            last = stream.read(1)
            # Don't loop forever
            if last == '' and proc.poll() is not None:
                break
            while last not in ['\n', '\r\n', '\r']:
                # Don't loop forever
                if last == '' and proc.poll() is not None:
                    break
                out.append(last)
                last = stream.read(1)
            out = ''.join(out)
            yield out


# ===========================================
# Batcher
# ===========================================

def _get_files(extension: str = "*") -> list:
    dir_path = _args.get("directory")
    if not dir_path:
        if debug_mod:
            dir_path = _dir_test_files
        else:
            raise RuntimeError("No directory path given !")
    
    dir_path = Path(dir_path)
    if not dir_path.exists():
        raise RuntimeError(f"Path {dir_path} does not exists !")
    if not dir_path.is_dir():
        raise RuntimeError(f"Path {dir_path} is not a directory!")
    
    return [str(file_path) for file_path in dir_path.glob(extension) if file_path.is_file()]


def _get_scenario_name() -> str:
    name = _args.get("name")
    if not name:
        if debug_mod:
            name = "printHodor"
        else:
            raise RuntimeError(f"Scenario {name} not found !")
    
    return name


def _get_all_scenario_names() -> list:
    return [x.with_suffix("").name for x in _scenarios_dir.glob("*.py") if x.is_file()]


def _create_scenario_file(scenario: str) -> Path:
    # Read maya stand alone file
    with _maya_stand_alone_path.open('r') as source_file:
        source_content = source_file.readlines()
    # Read scenario file
    scenario_file = _scenarios_dir / f"{scenario}.py"
    with scenario_file.open('r') as replacement_file:
        replacement_content = replacement_file.readlines()
    # Concatenate files
    start_index = None
    end_index = None
    for i, line in enumerate(source_content):
        if "### Start process" in line:
            start_index = i
        elif "### End process" in line and start_index is not None:
            end_index = i
            break
    if start_index is None or end_index is None:
        raise ValueError("Hodor !")
    new_content = source_content[:start_index + 1]
    new_content.extend(replacement_content)
    new_content.extend(source_content[end_index:]) 
    # Save batch file
    date = datetime.now().strftime("%m_%d_%Y_%Hh%Mmin")
    python_batch_path = _tmp_dir / f"{scenario}_{date}.py"
    with python_batch_path.open('w') as output_file:
        output_file.writelines(new_content)
    
    return python_batch_path


def main():
    scenario_name = _get_scenario_name()
    if scenario_name not in _get_all_scenario_names():
        raise RuntimeError(f'Scenario "{scenario_name}" not found !')

    tmp_file = _create_scenario_file(scenario_name)
    files = _get_files()
    for f in files:
        run_process(_get_cmd(f, tmp_file))

if __name__ == "__main__":
    main()
