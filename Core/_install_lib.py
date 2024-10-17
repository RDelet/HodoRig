from __future__ import annotations

import sys
import subprocess
from pathlib import Path

from ..Core import _process


_maya_dir = Path(sys.executable).parent
_mayapy = _maya_dir / "mayapy.exe"
module_names = ["numpy"]


def install():
    upgrade_cmd = f"\"{_mayapy}\" -m pip install --upgrade pip"
    _process.run(upgrade_cmd)

    for module_name in module_names:
        cmd = f"\"{_mayapy}\" -m pip install {module_name}"
        _process.run(cmd)
