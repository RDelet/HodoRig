from __future__ import annotations

from datetime import datetime
import logging
from pathlib import Path
import sys


from maya import cmds


_current_dir = Path(__file__)
_logLevel = logging.DEBUG
_kLoggerName = _current_dir.parent.name
__date_str = datetime.now().strftime("%m_%d_%Y_%Hh%Mmin")
_output_log = _current_dir.parent.parent / "Logs" / f"MAYA_LOG_{__date_str}.log"
with open(_output_log, "w") as f:
    f.write("")


# Formateur
_formatter_str = f"[{_kLoggerName} %(levelname)s] - "
_formatter_str += "[%(asctime)s] - [%(module)s.%(funcName)s, ln.%(lineno)d] -> %(message)s"
_formatter = logging.Formatter(_formatter_str)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(_formatter)

# Stream
stream_handler_out = logging.StreamHandler(stream=sys.stdout)
stream_handler_out.setLevel(_logLevel)
stream_handler_out.setFormatter(_formatter)

stream_handler_err = logging.StreamHandler(stream=sys.stderr)
stream_handler_err.setLevel(_logLevel)
stream_handler_err.setFormatter(_formatter)

# Output file
def _set_output_log():
    cmds.scriptEditorInfo(writeHistory=True, historyFilename={_output_log})
cmds.evalDeferred(_set_output_log)

# Logger
log = logging.getLogger(_kLoggerName)
log.setLevel(_logLevel)
log.addHandler(stream_handler_out)
log.addHandler(stream_handler_err)