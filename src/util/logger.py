from io import StringIO
from time import localtime, mktime, gmtime
import logging, sys


class Logger(logging.Logger):
    _buffer = None
    _format = f"%(asctime)s %(message)s"

    @classmethod
    def kst(cls, *args):
        return localtime(mktime(gmtime()) + 9 * 3600)

    def __init__(self, name: str):
        super().__init__(name=name, level=logging.INFO)
        self.propagate = False

        formatter = logging.Formatter(
            fmt=self._format,
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
    def formatter(self):
        return self._format

    @formatter.setter
    def formatter(self, formatter:str):
        self._format = formatter
        if formatter.startswith("%(asctime)s") or formatter.lower() == "default":
            formatter = logging.Formatter(fmt=formatter, datefmt="%Y-%m-%d %H:%M:%S")
            formatter.converter = self.kst
        for handler in self.handlers:
            handler.setFormatter(logging.Formatter(fmt=formatter))
        return

    @property
    def stream(self) -> str:
        return self._buffer.getvalue()

    def to_html(self):
        return self.stream \
               .replace("\n", "<br>") \
               .replace("  -", f'{"&nbsp;" * 4}-') \
               .replace("---", "<hr>")

    def clear(self):
        self._buffer.truncate(0)
        self._buffer.seek(0)
        return