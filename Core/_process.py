from __future__ import annotations

import contextlib
import subprocess

from ..Core.logger import log


def run(cmd: list | tuple):
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
            log.info(line)
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
