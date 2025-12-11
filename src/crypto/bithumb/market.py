if not "Ticker" in globals():
    from src.crypto.bithumb.ticker import Ticker
from collections import deque
from pandas import DataFrame, Series
from typing import Union
import pandas as pd
import requests


class Market:
    url: str = "https://api.bithumb.com/v1"
    headers = {"accept": "application/json"}

    rename = {
        'market': 'ticker',
        'english_name': 'name',
        # 'market_warning': 'warning',
        # 'korean_name': 'kor',
        'warning_type': 'warning',
        'end_date': 'warning_end'
    }

    def __init__(self):
        self._mem_ = deque(maxlen=5)
        return

    def __iter__(self):
        for ticker in self.tickers.index:
            yield ticker

    def _repr_html_(self):
        return getattr(self.tickers, '_repr_html_')()

    @classmethod
    def _fetch_(cls, url: str, **kwargs) -> Union[DataFrame, Series]:
        """
        url: https://api.bithumb.com 의 api 데이터 취득
        base url의 하위 주소를 입력하여 응답을 pandas Series 또는 DataFrame으로 변환

        Args:
            url     (str)   : 주소, base url이 제외된 하위 주소
            kwargs  (dict)  : Series 또는 DataFrame 변환 시 전달할 Keywoard Arguments

        Returns:
            Union[Series, DataFrame] :
        """
        resp = requests \
            .get(f"{cls.url}{url}", headers=cls.headers) \
            .json()
        return Series(resp[0], **kwargs) if len(resp) == 1 else DataFrame(resp, **kwargs)

    @classmethod
    def _fetch_tickers(cls) -> DataFrame:
        data = cls._fetch_('/market/all?isDetails=true')
        cols = {k: v for k, v in cls.rename.items() if k in data.columns}
        data = data.rename(columns=cols)[cols.values()]
        data = data[data['ticker'].str.startswith('KRW')]
        # data["warning"] = data["warning"].replace("NONE", None)
        return data.set_index(keys='ticker')

    @classmethod
    def _fetch_warnings(cls) -> DataFrame:
        data = cls._fetch_('/market/virtual_asset_warning')
        cols = {k: v for k, v in cls.rename.items() if k in data.columns}
        data = data.rename(columns=cols)[cols.values()]
        data = data[data['ticker'].str.startswith('KRW')]
        return data.set_index(keys='ticker')

    @property
    def baseline(self) -> DataFrame:
        if not self._mem_:
            self.update_baseline(period='min', unit=60)
        return list(self._mem_)[-1]

    @property
    def tickers(self) -> DataFrame:
        """
                            name	                          warning	        warning_end
        ticker
        KRW-BTC	         Bitcoin	                              NaN	                NaN
        KRW-ETH	        Ethereum	                              NaN	                NaN
        KRW-ETC	Ethereum Classic	                              NaN	                NaN
        KRW-XRP	             XRP	                              NaN	                NaN
        KRW-BCH	    Bitcoin Cash	                              NaN	                NaN
        ...	                 ...	                              ...	                ...
        KRW-MMT	        Momentum	                              NaN	                NaN
        KRW-MET	         Meteora	                              NaN	                NaN
        KRW-KITE	        Kite	                              NaN	                NaN
        KRW-TRUST	   Intuition	DEPOSIT_AMOUNT_SUDDEN_FLUCTUATION	2025-12-10 07:04:59
        KRW-PIEVERSE	Pieverse	                              NaN	                NaN
        450 rows × 3 columns
        """
        return self._fetch_tickers().join(self._fetch_warnings())

    def update_baseline(self, period: str = 'd', *args, **kwargs):
        fail = []
        objs = {}
        for ticker in self.tickers.index:
            try:
                objs[ticker] = Ticker(ticker).ohlcv(period=period, *args, **kwargs)
            except KeyError:
                fail.append(ticker)
                continue
        self._mem_.append(pd.concat(objs, axis=1).sort_index(ascending=True).tail(200))
        return fail

