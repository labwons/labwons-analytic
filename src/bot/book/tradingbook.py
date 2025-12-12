if not "Ticker" in globals():
    from src.crypto.bithumb.ticker import Ticker
from datetime import datetime
from zoneinfo import ZoneInfo
from pandas import DataFrame
from numpy import nan
import pandas as pd
import os


SCHEMA = {
    'ticker': { 'index': True, 'dtype': str , 'default': ''},
    'status': {'index': False, 'dtype': str, 'default': ''},
    'current_price': {'index': False, 'dtype': float, 'default': nan},
    'current_amount': {'index': False, 'dtype': float, 'default': nan},
    'current_volume': {'index': False, 'dtype': float, 'default': nan},
    'buy_price': {'index': False, 'dtype': float, 'default': nan},
    'buy_time': {'index': False, 'dtype': str, 'default': ''},
    'sell_price': {'index': False, 'dtype': float, 'default': nan},
    'sell_time': {'index': False, 'dtype': str, 'default': ''},
    'signal': {'index': False, 'dtype': str, 'default': ''},
    'signaled_time': {'index': False, 'dtype': str, 'default': ''},
    'signal_elapsed_time': {'index': False, 'dtype': float, 'default': nan},
    'signaled_price': {'index': False, 'dtype': float, 'default': nan},
    'signaled_amount': {'index': False, 'dtype': float, 'default': nan},
    'signaled_volume': {'index': False, 'dtype': float, 'default': nan},
    'yield_confirmed': {'index': False, 'dtype': float, 'default': nan},
    'yield_elapsed': {'index': False, 'dtype': float, 'default': nan},
    'yield_1h_from_detected': {'index': False, 'dtype': float, 'default': nan},
    'yield_4h_from_detected': {'index': False, 'dtype': float, 'default': nan},
    'yield_12h_from_detected': {'index': False, 'dtype': float, 'default': nan},
    'yield_24h_from_detected': {'index': False, 'dtype': float, 'default': nan},
    'yield_36h_from_detected': {'index': False, 'dtype': float, 'default': nan},
    'yield_48h_from_detected': {'index': False, 'dtype': float, 'default': nan},
    'yield_60h_from_detected': {'index': False, 'dtype': float, 'default': nan},
    'yield_72h_from_detected': {'index': False, 'dtype': float, 'default': nan},
}
STATUS = [
    "WATCH",
    "HOLD",
    "BID",
    "ASK",
    "SELL"
]
class TradingBook:

    _filename:str = 'book.json'
    try:
        _basepath:str = os.path.dirname(__file__)
    except NameError:
        _basepath:str = os.getcwd()
    _filepath:str = os.path.join(_basepath,_filename)

    def __init__(self, readonly:bool=False):
        if readonly:
            self.book = pd.read_json(
                "https://raw.githubusercontent.com"
                "/labwons"
                "/labwons-analytic"
                "/refs"
                "/heads"
                "/main"
                "/src"
                "/bot"
                "/book"
                "/book.json"
            )
        else:
            if not os.path.isfile(self._filepath):
                self.book = DataFrame(columns=list(SCHEMA.keys())).set_index(keys='ticker')
            else:
                self.book = pd.read_json(self._filepath, orient="index")
        return

    def __repr__(self):
        return repr(self.book)

    def __str__(self):
        return str(self.book)

    def __getattr__(self, item):
        return getattr(self.book, item)

    def __getitem__(self, item):
        return self.book[item]

    def __setitem__(self, key, value):
        return self.book.__setitem__(key, value)

    def _repr_html_(self):
        return getattr(self.book, '_repr_html_')()

    def append(self, ticker:str, **kwargs):
        new = DataFrame(
            index=[ticker],
            data=[{
                key: kwargs.get(key, schema['default']) for key, schema in SCHEMA.items()
            }]
        )
        self.book = pd.concat([self.book, new.drop(columns=['ticker'])], axis=0)
        return

    def update(self):
        kst = datetime.now(tz=ZoneInfo('Asia/Seoul'))
        for ticker in self.index:
            coin = Ticker(ticker=ticker)
            time = datetime.strptime(self.loc[ticker, 'signaled_time'], '%Y-%m-%dT%H:%M:%S')
            self.loc[ticker, 'current_price'] = coin['trade_price']
            self.loc[ticker, 'current_amount'] = coin['acc_trade_price_24h']
            self.loc[ticker, 'current_volume'] = coin['acc_trade_volume_24h']
            # self.loc[ticker]
        self['yield_confirmed'] = (self['sell_price'] - self['buy_price']) / self['buy_price'] * 100
        self['yield_elapsed'] = (self['current_price'] - self['signaled_price']) / self['signaled_price'] * 100
        return

    def save(self):
        keys = list(SCHEMA.keys())
        keys.remove('ticker')
        self[keys].to_json(self._filepath, orient="index")
        return
