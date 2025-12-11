if not "Schema" in globals():
    from src.bot.book.schema import Schema
from pandas import DataFrame, Series
import pandas as pd
import os


SCHEMA = Schema()
class TradingBook:

    _filename:str = 'book.json'
    try:
        _basepath:str = os.path.dirname(__file__)
    except NameError:
        _basepath:str = os.getcwd()
    _filepath:str = os.path.join(_basepath,_filename)
    def __init__(self):
        if not os.path.isfile(self._filepath):
            self.book = DataFrame(columns=SCHEMA.columns)
        else:
            self.book = pd.read_json(self._filepath)
        return

    def __repr__(self):
        return repr(self.book)

    def __str__(self):
        return str(self.book)

    def __setattr__(self, name, value):
        if name in SCHEMA.columns:
            self.book.at[self.book.index[-1], name] = value
        else:
            super().__setattr__(name, value)
        return

    def _repr_html_(self):
        return getattr(self.book, '_repr_html_')()

    def append(self, ticker:str):
        name = 0 if self.book.empty else self.book.index[-1] + 1
        obj = Series(index=SCHEMA.columns, name=name, dtype='object')
        obj['ticker'] = ticker
        self.book = pd.concat([self.book, obj.to_frame().T])
        return

    def save(self):
        self.book.to_json(self._filepath)
        return


if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    book = TradingBook()
    print(book)