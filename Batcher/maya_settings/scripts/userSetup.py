from pathlib import Path
import sys

_current_dir = Path(__file__)
_module_dir = _current_dir.parent.parent.parent.parent
sys.path.insert(0, str(_module_dir))

import HodoRig
