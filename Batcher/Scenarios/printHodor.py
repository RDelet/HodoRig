import argparse
from pathlib import Path


_file_name = Path(__file__).with_suffix("").name
parser = argparse.ArgumentParser(description=f"Maya Scenario {_file_name}", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", help="Scenario file")
_args = vars(parser.parse_args())


def _get_file() -> str:
    try:
        return Path(_args.get("file"))
    except Exception as e:
        raise RuntimeError("Error on retrieve scenario file !") from e


def process():
    file_path = _get_file()
    print(f"###################\tHodor | {file_path}")
