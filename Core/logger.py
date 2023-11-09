import sys
import logging


_kLoggerName = "Hodo Rig"
_formatter_str = f"[{_kLoggerName} %(levelname)s] - "
_formatter_str += "[%(asctime)s] - [%(module)s.%(funcName)s, ln.%(lineno)d] -> %(message)s"
_formatter = logging.Formatter(_formatter_str)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(_formatter)


stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(_formatter)

log = logging.getLogger(_kLoggerName)
log.setLevel(logging.INFO)
log.addHandler(stream_handler)
log.propagate = False