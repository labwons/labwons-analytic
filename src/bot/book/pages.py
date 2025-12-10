from src.bot.book.schema import Schema
from pandas import DataFrame
import pandas as pd
import os


SCHEMA = Schema()
class TradingBook:

    _filename:str = 'book.json'
    _basepath:str = os.path.dirname(__file__)
    _filepath:str = os.path.join(_basepath,_filename)
    def __init__(self):
        if not os.path.isfile(self._filepath):
            self.book = DataFrame(columns=SCHEMA.columns, index=[0])
            self.book.to_json(self._filepath)
        else:
            self.book = pd.read_json(self._filepath)
        return

    def __repr__(self):
        return repr(self.book)

    def __str__(self):
        return str(self.book)

    def _repr_html_(self):
        return getattr(self.book, '_repr_html_')()


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    book = TradingBook()
    print(book)