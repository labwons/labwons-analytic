if not "Indicator" in globals():
    from src.analysis.indicator import Indicator
from pandas import Series, DataFrame
import pandas as pd
import os


class Strategy(Indicator):

    def __init__(self, baseline: DataFrame):
        super().__init__(baseline)
        if '__file__' in globals():
            _dir = os.path.join(os.path.dirname(__file__), 'log')
        else:
            _dir = os.path.join(os.getcwd(), 'log')
        os.makedirs(_dir, exist_ok=True)
        self.file = file = os.path.join(_dir, 'signal.parquet')
        if os.path.exists(file):
            self.db = pd.read_parquet(file, engine='pyarrow')
        else:
            self.db = DataFrame()
        return

    def log(self, name:str, signal:DataFrame):

        return

    def squeeze_expand(
        self,
        window_width:int=100,
        width_threshold:float=0.1,
        window_volume:int=20,
    ):
        # 변동성 확대 국면 파악
        self['bb_squeeze'] = self['bb_width'] \
                             .rolling(window=window_width) \
                             .apply(lambda x:Series(x).rank(pct=True).iloc[-1], raw=False) < width_threshold
        self['bb_squeeze_release'] = self['bb_squeeze'].shift(1) & (~self['bb_squeeze'])
        self['bb_breakout'] = self['close'] > self['bb_upper']
        self['volume_spike'] = self['volume'] > self['volume'].rolling(window_volume).mean()
        self['sig_squeeze_expand'] = (
            self['bb_squeeze_release'] &
            self['bb_breakout'] &
            self['volume_spike']
        )
        del self['bb_squeeze']
        del self['bb_squeeze_release']
        del self['bb_breakout']
        del self['volume_spike']

        return self['sig_squeeze_expand'].astype(int).replace(0, None)

    def drawdown_recover(
        self,
        basis:str='tp',
        window:int=36,
        drawdown_threshold:float=-0.1,
        drawdown_recover_threshold:float=0.3,
        drawdown_rapid:int=3,
    ):
        self['dd_max'] = self[basis].rolling(window=window).max()
        self['dd_min'] = self[basis].rolling(window=window).min()
        self['dd_height'] = self['dd_min'] / self['dd_max'] - 1
        self['dd_recover'] = (self[basis] - self['dd_min']) / (self['dd_max'] - self['dd_min'])
        self['dd_rapid'] = (
                (self['close'].pct_change(1, fill_method=None) <= (drawdown_threshold / 3)) |
                (self['close'].pct_change(drawdown_rapid, fill_method=None) <= (drawdown_threshold / 2))
        ).astype(int)
        self['dd_occur'] = self['dd_rapid'].rolling(window).sum() == 1

        self['is_macd_pos'] = (self['macd_diff'] >= 0).astype(bool)
        self['macd_cross'] = (self['is_macd_pos']) & (~self['is_macd_pos'].shift(1))

        self['sig_drawdown_recover'] = (
            (self['dd_height'] <= drawdown_threshold) &
            (self['dd_recover'] <= drawdown_recover_threshold) &
            self['dd_occur'] &
            self['macd_cross']
        )

        del self['dd_max']
        del self['dd_min']
        del self['dd_height']
        del self['dd_recover']
        del self['dd_rapid']
        del self['dd_occur']
        del self['is_macd_pos']
        del self['macd_cross']

        return self['sig_drawdown_recover'].astype(int).replace(0, None)

