from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import sys

from maya import cmds


_current_dir = Path(__file__)
_log_dir = _current_dir.parent.parent / "Logs"
if not _log_dir.exists():
    _log_dir.mkdir(parents=True, exist_ok=True)

_logLevel = logging.DEBUG
_kLoggerName = _current_dir.parent.name
__date_str = datetime.now().strftime("%m_%d_%Y_%Hh%Mmin")

# Create output file
_output_log = _current_dir.parent.parent / "Logs" / f"MAYA_LOG_{__date_str}.log"
with open(_output_log, "w") as f:
    f.write("")

# Formateur
_formatter_str = f"[{_kLoggerName} %(levelname)s] - "
_formatter_str += "[%(asctime)s] - [%(module)s.%(funcName)s, ln.%(lineno)d] -> %(message)s"
_formatter = logging.Formatter(_formatter_str)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(_formatter)

# Handler
stream_handler_err = logging.StreamHandler(stream=sys.stderr)
stream_handler_err.setLevel(_logLevel)
stream_handler_err.setFormatter(_formatter)

file_handler = logging.FileHandler(_output_log)
file_handler.setLevel(_logLevel)
file_handler.setFormatter(_formatter)

# Logger
log = logging.getLogger(_kLoggerName)
log.setLevel(_logLevel)
log.addHandler(stream_handler_err)
log.addHandler(file_handler)

# ScriptEditor output
def _set_output_log():
    cmds.scriptEditorInfo(writeHistory=True, historyFilename=_output_log)
cmds.evalDeferred(_set_output_log)