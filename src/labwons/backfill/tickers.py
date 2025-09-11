from labwons.util import DATETIME, PATH
from labwons.fetch import MarketSectors
import pandas as pd
import os


def BackfillTickers(date:str=''):
    wise = date
    if wise == DATETIME.TRADING:
        wise = DATETIME.WISE
    sectors = MarketSectors.fetch(wise)
    
    if not date:
        date = DATETIME.TRADING

    # merge = sectors.join()
    sectors.to_parquet(f'{PATH.TICKERS}/{date}.parquet', engine='pyarrow')
    return