if not "Indicator" in globals():
    from src.analysis.indicator import Indicator
from datetime import datetime
from pandas import DataFrame, Series
from zoneinfo import ZoneInfo
import pandas as pd


class Strategy(Indicator):

    @staticmethod
    def to_report(sig: DataFrame) -> DataFrame:
        lap = pd.to_datetime(datetime.now(ZoneInfo('Asia/Seoul'))).tz_localize(None)
        sig = sig[pd.to_datetime(sig.index) >= (lap - pd.Timedelta(hours=48))]
        sig.columns = [c.replace("KRW-", "") for c in sig.columns]
        sig = sig.apply(lambda row: ','.join(sig.columns[row.notna()]), axis=1) \
                 .replace("", None) \
                 .dropna()
        if isinstance(sig, Series):
            sig = sig.to_frame(name='Detected')
            sig.index.name = ''
        return sig

    def squeeze_expand(
        self,
        width_mode: str = 'min',
        width_window: int = 7,
        volume_window: int = 7
    ):
        # 밴드 폭 전략
        # @width_mode == 'min':
        #     @width_window에 대해 최소 값인 경우
        #     * 단기 가격 변동성을 고려할 때 사용
        # @width_mode == 'lower':
        #     @width_rank 보다 작은 경우
        #     * 중자아기 가격 변동성을 고려할 때 사용
        if width_mode == 'min':
            self['sig_squeeze_expand'] = (
                (self['bb_width'] == self['bb_width'].rolling(width_window).min()) &
                (self['close'] >= self['bb_upper']) &
                ((self['close'] - self['open']) >= (self['bb_upper'] - self['mid'])) &
                (self['volume'] >= self['volume'].rolling(volume_window).mean())
            ).astype(int).replace(0, None)
        elif width_mode == 'lower':
            pass
        else:
            raise KeyError
        return self['sig_squeeze_expand']

# coins = Coins()
# strategy = Strategy(coins.baseline)
# strategy.install()
# strategy.squeeze_expand()
# strategy.to_report(strategy['sig_squeeze_expand'])

