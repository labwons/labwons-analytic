from io import StringIO
from time import localtime, mktime, gmtime
import logging, sys


class Logger(logging.Logger):
    _runtime = None
    _buffer = None

    @classmethod
    def kst(cls, *args):
        return localtime(mktime(gmtime()) + 9 * 3600)

    def __init__(self, name: str):
        super().__init__(name=name, level=logging.INFO)
        self.propagate = False
        formatter = logging.Formatter(
            fmt=f"%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        formatter.converter = self.kst

        stream = logging.StreamHandler(stream=sys.stdout)
        stream.setLevel(logging.INFO)
        stream.setFormatter(formatter)
        self.addHandler(stream)

        self._buffer = StringIO()
        memory = logging.StreamHandler(stream=self._buffer)
        memory.setLevel(logging.INFO)
        memory.setFormatter(formatter)
        self.addHandler(memory)
        return

    def __call__(self, msg: str):
        self.info(msg=msg)
        return

    @property
    def stream(self) -> str:
        return self._buffer.getvalue()

    def clear(self):
        self._buffer.truncate(0)
        self._buffer.seek(0)
        return