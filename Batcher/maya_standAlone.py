import os
from pathlib import Path

from maya import standalone


_current_dir = Path(__file__)
_maya_settings_dir = _current_dir.parent.parent / "maya_settings"
os.environ["MAYA_APP_DIR"] = str(_maya_settings_dir)


def pre_process():
    try:
        standalone.initialize("python")
        print("Maya is initialized.")
    except Exception as e:
        raise RuntimeError("Error on initialize maya") from e


### Start process
def process():
    pass
### End process


def post_process():
    try:
        standalone.uninitialize()
        print("Maya is uninitialize.")
    except Exception as e:
        raise RuntimeError("Error on uninitialize maya") from e


def main():
    pre_process()
    process()
    post_process()


if __name__ == "__main__":
    main()