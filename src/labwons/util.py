from labwons.dtypes import classproperty

from datetime import datetime, timedelta
from pytz import timezone
from pykrx.stock import get_nearest_business_day_in_a_week as get_td
from typing import Dict, Union


TIMEZONE = timezone('Asia/Seoul')
def CLOCK(strfmt: str = '') -> Union[str, datetime]:
    return datetime.now(TIMEZONE).strftime(strfmt) if strfmt else datetime.now(TIMEZONE)

class DATETIME:

    TODAY:str = CLOCK("%Y%m%d")

    @classproperty
    def TRADING(cls) -> str:
        if not hasattr(cls, f'_TD_{cls.TODAY}'):
            try:
                setattr(cls, f'_TD_{cls.TODAY}', get_td(cls.TODAY))
            except (KeyError, Exception):
                return ''
        return getattr(cls, f'_TD_{cls.TODAY}')

    @classmethod
    def get_previous_trading_dates(cls, *previous_days) -> Dict[str, str]:
        if not previous_days:
            previous_days = [1, 7, 14, 30, 61, 92, 183, 365]
        td = datetime.strptime(cls.TRADING, '%Y%m%d')
        return {f'D-{n}': get_td((td - timedelta(n)).strftime("%Y%m%d")) for n in previous_days}

    @classmethod
    def is_market_open(cls) -> bool:
        return (cls.TODAY == cls.TRADING) and (900 <= int(CLOCK("%H%M")) <= 1530)

    @classmethod
    def delta_today(cls, days:int):
        cls.TODAY = (CLOCK() - timedelta(days)).strftime('%Y%m%d')
        return


if __name__ == "__main__":
    print(DATETIME.TODAY)
    DATETIME.delta_today(1)
    print(DATETIME.TODAY)


