import os

from HodoRig.Core.logger import log

debug_py = False
try:
    import debugpy
    debug_py = True
except Exception:
    log.warning("Module debugpy is not installed.")


def vs_code(port: int = 53001):
    if not debug_py:
        raise RuntimeError("No module debugpy found !")

    mayapy_exe = os.path.join(os.environ.get("MAYA_LOCATION"), "bin", "mayapy")
    debugpy.configure(python=mayapy_exe)
    debugpy.listen(port)
