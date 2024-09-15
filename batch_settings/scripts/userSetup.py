import os
import sys

# Init current module
dir, _ = os.path.split(__file__)
module_dir = os.path.normpath(os.path.join(dir, "../"))
sys.path.insert(0, module_dir)

import HodoRig