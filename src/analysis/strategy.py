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
        window_width:int=100,
        width_threshold:float=0.2,
        window_volume:int=20,
    ):
        # 변동성 확대 국면 파악
        self['bb_width_pct'] = self['bb_width'] \
                               .rolling(window=window_width) \
                               .apply(lambda x:Series(x).rank(pct=True).iloc[-1], raw=False)
        self['bb_squeeze'] = self['bb_width_pct'] < width_threshold
        self['bb_squeeze_release'] = self['bb_squeeze'].shift(1) & (~self['bb_squeeze'])
        self['bb_breakout'] = self['close'] > self['bb_upper']
        self['volume_spike'] = self['volume'] > self['volume'].rolling(window_volume).mean()
        self['sig_squeeze_expand'] = (self['bb_squeeze_release'] & self['bb_breakout'] & self['volume_spike'])

        del self['bb_width_pct']
        del self['bb_squeeze']
        del self['bb_squeeze_release']
        del self['bb_breakout']
        del self['volume_spike']
        return self['sig_squeeze_expand'].astype(int).replace(0, None)

    def up_trend(
        self,
        window:int=3
    ):
        # 상승 추세 Zone 파악
        self['bb_in_zone'] = (self['close'] >= self['tr_upper']) & (self['close'] <= self['bb_upper'])
        self['bb_in_zone_window'] = self['bb_in_zone'].rolling(window).sum() == window
        self['bb_out_zone'] = self['bb_in_zone'].shift(window) == False
        self['sig_up_trend'] = self['bb_in_zone_window'] & self['bb_out_zone']

        del self['bb_in_zone']
        del self['bb_in_zone_window']
        del self['bb_out_zone']
        return self['sig_up_trend'].astype(int).replace(0, None)

