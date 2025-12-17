if not "Indicator" in globals():
    from src.analysis.indicator import Indicator
from pandas import Series


class Strategy(Indicator):

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
        # Deprecated

        # 상승 추세 Zone 파악
        self['bb_in_zone'] = (self['close'] >= self['tr_upper']) & (self['close'] <= self['bb_upper'])
        self['bb_in_zone_window'] = self['bb_in_zone'].rolling(window).sum() == window
        self['bb_out_zone'] = self['bb_in_zone'].shift(window) == False
        self['sig_up_trend'] = self['bb_in_zone_window'] & self['bb_out_zone']

        del self['bb_in_zone']
        del self['bb_in_zone_window']
        del self['bb_out_zone']
        return self['sig_up_trend'].astype(int).replace(0, None)

    def drawdown_recover(
        self,
        basis:str='tp',
        window:int=36,
        drawdown_threshold:float=-0.1,
        drawdown_recover_threshold:float=0.3,
        drawdown_rapid:int=3,
    ):
        self['_dd_max'] = self[basis].rolling(window=window).max()
        self['_dd_min'] = self[basis].rolling(window=window).min()
        self['_dd_height'] = self['_dd_min'] / self['_dd_max'] - 1
        self['_dd_recover'] = (self[basis] - self['_dd_min']) / (self['_dd_max'] - self['_dd_min'])
        self['_dd_rapid'] = (
                (self['close'].pct_change(1, fill_method=None) <= (drawdown_threshold / 3)) |
                (self['close'].pct_change(drawdown_rapid, fill_method=None) <= (drawdown_threshold / 2))
        ).astype(int)
        self['_dd_occur'] = self['_dd_rapid'].rolling(window).sum() == 1

        self['_is_macd_pos'] = self['macd_diff'] >= 0
        self['_macd_cross'] = (self['_is_macd_pos']) & (~self['_is_macd_pos'].shift(1).astype(bool))

        self['sig_drawdown_recover'] = (
            (self['_dd_height'] <= drawdown_threshold) &
            (self['_dd_recover'] <= drawdown_recover_threshold) &
            self['_dd_occur'] &
            self['_macd_cross']
        )

        del self['_dd_max']
        del self['_dd_min']
        del self['_dd_height']
        del self['_dd_recover']
        del self['_dd_rapid']
        del self['_is_macd_pos']
        del self['_macd_cross']
        del self['_dd_occur']

        return self['sig_drawdown_recover'].astype(int).replace(0, None)

