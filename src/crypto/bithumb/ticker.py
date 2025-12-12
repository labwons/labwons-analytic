if not "constrain" in globals():
    from src.util.deco import constrain
if not "Logger" in globals():
    from src.util.logger import Logger
from pandas import DataFrame, Series
from typing import Union
import pandas as pd
import requests


class Ticker:

    url:str = "https://api.bithumb.com/v1"
    headers = {"accept": "application/json"}
    rename = {
        "candle_date_time_kst": "datetime",
        "opening_price": "open",
        "high_price": "high",
        "low_price": "low",
        "trade_price": "close",
        "candle_acc_trade_price": "amount",
        "candle_acc_trade_volume": "volume",
        "trade_volume": 'volume',
        "ask_bid": "quote",
        "datetime": "datetime"
    }

    def __init__(self, ticker: str):
        self.ticker = ticker
        self._snap = Series()
        return

    def __repr__(self):
        return repr(self.snapShot)

    def __getitem__(self, item):
        if self._snap.empty:
            self._snap = self.snapShot
        return self._snap[item]

    @classmethod
    def _fetch_(cls, url:str, **kwargs) -> Union[DataFrame, Series]:
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

    @property
    def snapShot(self) -> Series:
        """
        market                               KRW-BTC
        trade_date                          20251128
        trade_time                            021901
        trade_date_kst                      20251128
        trade_time_kst                        111901
        trade_timestamp                1764328741157
        opening_price                      135796000
        high_price                         137125000
        low_price                          135372000
        trade_price                        135442000
        prev_closing_price                 135796000
        change                                  FALL
        change_price                          354000
        change_rate                           0.0026
        signed_change_price                  -354000
        signed_change_rate                   -0.0026
        trade_volume                        0.000073
        acc_trade_price           29804029073.873871
        acc_trade_price_24h      111366853330.307678
        acc_trade_volume                  218.675501
        acc_trade_volume_24h              815.641639
        highest_52_week_price              179734000
        highest_52_week_date              2025-10-10
        lowest_52_week_price               110000000
        lowest_52_week_date               2024-12-04
        timestamp                      1764328741157
        Name: KRW-BTC, dtype: object
        """
        self._snap = self._fetch_(f"/ticker?markets={self.ticker}", name=self.ticker)
        return self._snap

    @constrain('1minutes', '3minutes', '5minutes', '10minutes',
               '15minutes', '30minutes', '60minutes', '240minutes',
               '1days', '1weeks', '1months')
    def ohlcv(self, interval:str) -> DataFrame:
        """
                                 open	     high	      low	    close	      amount	     volume
        datetime
        2025-12-08T14:30:00	135976000	136192000	135976000	136032000	3.107575e+08	 2283670.13
        2025-12-08T14:00:00	135976000	136167000	135544000	135975000	1.790029e+09	13176614.54
        2025-12-08T13:30:00	135948000	136185000	135811000	135977000	1.024618e+09	 7535912.03
        2025-12-08T13:00:00	135782000	136038000	135700000	135948000	7.361658e+08	 5419830.47
        2025-12-08T12:30:00	136113000	136113000	135702000	135761000	1.072309e+09	 7893673.71
        ...	...	...	...	...	...	...
        2025-12-04T13:00:00	139211000	139232000	138978000	139048000	1.259391e+09	 9056382.13
        2025-12-04T12:30:00	139232000	139250000	138999000	139199000	1.363260e+09	 9800596.39
        2025-12-04T12:00:00	139559000	139650000	139160000	139244000	1.809427e+09	12977284.73
        2025-12-04T11:30:00	139374000	139618000	139148000	139559000	2.374796e+09	17033654.61
        2025-12-04T11:00:00	138590000	139590000	138500000	139374000	4.618125e+09	33227210.66
        200 rows × 6 columns

        :param interval:
        :param count:
        :return:
        """
        if interval.endswith('minutes'):
            query = f'/candles/minutes/{interval.replace("minutes", "")}?market={self.ticker}&count=200'
        else:
            query = f'/candles/{interval[1:]}?market={self.ticker}&count=200'

        data = self._fetch_(query)
        if isinstance(data, Series):
            raise KeyError
        cols = {k: v for k, v in self.rename.items() if k in data.columns}
        data = data.rename(columns=cols)[cols.values()]
        data = data.set_index(keys='datetime')
        data['volume'] = data['volume'] * 1e+6
        return data

    def execution(self, count: int = 100) -> DataFrame:
        """
        체결 내역

                                close	  volume  quote
        datetime
        2025-12-08 14:42:39	136108000	0.005988	BID
        2025-12-08 14:42:39	136100000	0.003500	BID
        2025-12-08 14:42:39	136099000	0.000087	BID
        2025-12-08 14:42:39	136082000	0.003211	BID
        2025-12-08 14:42:21	136082000	0.000050	BID
        ...	...	...	...
        2025-12-08 14:39:29	136101000	0.000073	ASK
        2025-12-08 14:39:29	136107000	0.001832	BID
        2025-12-08 14:39:18	136107000	0.003049	BID
        2025-12-08 14:39:10	136107000	0.000004	ASK
        2025-12-08 14:39:07	136108000	0.000062	ASK
        100 rows × 3 columns

        :param count:
        :return:
        """
        data = self._fetch_(f'/trades/ticks?market={self.ticker}&count={min(count, 500)}')
        data['datetime'] = pd.to_datetime(data['trade_date_utc'].astype(str) + ' ' + data['trade_time_utc'].astype(str))
        data['datetime'] = data['datetime'] + pd.Timedelta(hours=9)
        cols = {k: v for k, v in self.rename.items() if k in data.columns}

        data = data.rename(columns=cols)[cols.values()]
        data = data.set_index(keys='datetime')
        return data

    def order(self) -> DataFrame:
        """
        주문 내역

                            ask_price	bid_price  ask_size  bid_size
        datetime
        2025-12-08 14:43:42	136107000	136082000	 0.0012    0.0007
        2025-12-08 14:43:42	136108000	136059000	 0.0356	   0.0735
        2025-12-08 14:43:42	136109000	136026000	 0.1031	   0.0043
        2025-12-08 14:43:42	136112000	136025000	 0.0328	   0.0346
        2025-12-08 14:43:42	136117000	136014000	 0.0036	   0.0029
        ... ... ... ... ...
        2025-12-08 14:43:42	136182000	135977000	 0.0038	   0.0588
        2025-12-08 14:43:42	136185000	135976000	 0.0093	   0.0907
        2025-12-08 14:43:42	136186000	135975000	 0.0322	   0.1778
        2025-12-08 14:43:42	136188000	135974000	 0.0007	   0.0000
        2025-12-08 14:43:42	136192000	135973000	 0.0010	   0.0722
        :return:
        """
        base = self._fetch_(f'/orderbook?markets={self.ticker}')
        data = DataFrame(base['orderbook_units'])
        data['datetime'] = pd.to_datetime(base['timestamp'], unit='ms') + pd.Timedelta(hours=9)
        data['datetime'] = data['datetime'].dt.strftime("%Y-%m-%d %H:%M:%S")
        return data.set_index(keys='datetime')

    def to_logger(self, logger:Logger):
        ticker = self.ticker.replace('KRW-', '')
        logger(f'TICKER: <a href="https://m.bithumb.com/react/trade/chart/{ticker}-KRW">{ticker}</a>')
        logger(f'  - 현재가: {self["trade_price"]}원')
        logger(f'  - 등락률: {100 * self["signed_change_rate"]:.2f}%')
        logger(f'  - 거래대금: {self["acc_trade_price_24h"] / 1e+8:.2f}억원')
        logger(f'---')
        return