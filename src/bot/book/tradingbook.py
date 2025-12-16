if not "Ticker" in globals():
    from src.crypto.bithumb.ticker import Ticker
from datetime import datetime, timedelta
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
    'signaled_price': {'index': False, 'dtype': float, 'default': nan},
    'signal_reported_price': {'index': False, 'dtype': float, 'default': nan},
    'signaled_amount': {'index': False, 'dtype': float, 'default': nan},
    'signaled_volume': {'index': False, 'dtype': float, 'default': nan},
    'yield_confirmed': {'index': False, 'dtype': float, 'default': nan},
    'yield_ongoing': {'index': False, 'dtype': float, 'default': nan},
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
                if self.book.empty:
                    self.book = DataFrame(columns=list(SCHEMA.keys())).set_index(keys='ticker')
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
        for ticker in self.index:
            coin = Ticker(ticker=ticker)
            data = coin.ohlcv(interval='60minutes')

            s_price = book.loc[ticker, 'signaled_price']
            s_time = datetime.strptime(book.loc[ticker, 'signaled_time'], '%Y-%m-%dT%H:%M:%S')
            for h in [1, 4, 12, 24, 36, 48, 60, 72]:
                e_time = s_time + timedelta(hours=h)
                if e_time.strftime('%Y-%m-%dT%H:%M:%S') not in data.index:
                    continue
                price_at_time = data.loc[e_time.strftime('%Y-%m-%dT%H:%M:%S'), 'close']
                book.loc[ticker, f'yield_{h}h_from_detected'] = 100 * (price_at_time - s_price) / s_price

            book.loc[ticker, 'current_price'] = curr = coin['trade_price']
            book.loc[ticker, 'current_amount'] = data.iloc[-1]['amount']
            book.loc[ticker, 'current_volume'] = data.iloc[-1]['volume']
            book.loc[ticker, 'yield_ongoing'] = 100 * (curr - s_price) / s_price
        return

    def save(self):
        keys = list(SCHEMA.keys())
        keys.remove('ticker')
        self[keys].to_json(self._filepath, orient="index")
        return

if __name__ == "__main__":
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    book = TradingBook()
    print(book)