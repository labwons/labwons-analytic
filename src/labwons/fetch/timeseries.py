from labwons.util import DATETIME

from datetime import timedelta
from pandas import DataFrame
from pykrx.stock import (
    get_market_ohlcv_by_date,
    get_exhaustion_rates_of_foreign_investment_by_date
)


def get_ohlcv(ticker:str) -> DataFrame:
    _ohlcv = get_market_ohlcv_by_date(
        fromdate='19900101',
        todate=DATETIME.TODAY,
        ticker=ticker,
        freq='d'
    )

    trade_stop = _ohlcv[_ohlcv.시가 == 0].copy()
    if not trade_stop.empty:
        _ohlcv.loc[trade_stop.index, ['시가', '고가', '저가']] = trade_stop.종가
    _ohlcv.index.name = 'date'
    return _ohlcv.rename(columns=dict(시가='open', 고가='high', 저가='low', 종가='close', 거래량='volume'))

def get_foreign_rate(ticker:str) -> DataFrame:
    return get_exhaustion_rates_of_foreign_investment_by_date(
        fromdate='19900101',
        todate=DATETIME.TODAY,
        ticker=ticker,
    )

