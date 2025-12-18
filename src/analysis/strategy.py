if not "Indicator" in globals():
    from src.analysis.indicator import Indicator
from pandas import Series, DataFrame
import pandas as pd


class Strategy(Indicator):

    @staticmethod
    def describe(signal:DataFrame):
        signaled = []
        for ticker in signal.columns:
            unit = signal[ticker].dropna()
            if unit.empty:
                continue
            signaled.append(unit)
        return pd.concat(signaled, axis=1).sort_index(ascending=True)

    def squeeze_expand(
        self,
        window_width:int=100,
        width_threshold:float=0.1,
        window_volume:int=20,
        describe:bool=True,
    ) -> DataFrame:
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
        sig = self['sig_squeeze_expand'].astype(int).replace(0, None)
        if not describe:
            return sig
        return self.describe(signal=sig)

    def drawdown_recover(
        self,
        basis:str='tp',
        window:int=36,
        drawdown_threshold:float=-0.1,
        drawdown_recover_threshold:float=0.3,
        drawdown_rapid:int=3,
        describe:bool=True,
    ) -> DataFrame:
        self['dd_max'] = self[basis].rolling(window=window).max()
        self['dd_min'] = self[basis].rolling(window=window).min()
        self['dd_rapid'] = (
                (self['close'].pct_change(1, fill_method=None) <= (drawdown_threshold / 3)) |
                (self['close'].pct_change(drawdown_rapid, fill_method=None) <= (drawdown_threshold / 2))
        ).astype(int)
        self['dd_occur'] = (
            # 급락 감지
            (
                # 종가 기준 1봉 변화량이 허용 낙폭을 넘어갈 때
                (self['close'].pct_change(1, fill_method=None) <= (drawdown_threshold / 3)) |
                # 종가 기준 n봉
            )
            
            
            
           (self['dd_rapid'].rolling(window).sum() >= 1) &
           ((self['dd_min'] / self['dd_max'] - 1) <= drawdown_threshold) &
           ((self['close'] > self['tr_upper']).astype(int).rolling(window).sum() >= 1)
        )
        self['dd_recover'] = (self[basis] - self['dd_min']) / (self['dd_max'] - self['dd_min'])

        self['is_macd_pos'] = self['macd_diff'] >= 0
        self['macd_cross'] = self['is_macd_pos'] & (~self['is_macd_pos'].shift(1).astype(bool))

        self['sig_drawdown_recover'] = (
            self['dd_occur'] &
            (self['dd_recover'] <= drawdown_recover_threshold) &
            self['macd_cross']
        )

        del self['dd_max']
        del self['dd_min']
        del self['dd_recover']
        del self['dd_rapid']
        del self['dd_occur']
        del self['is_macd_pos']
        del self['macd_cross']
        sig = self['sig_drawdown_recover'].astype(int).replace(0, None)
        if not describe:
            return sig
        return self.describe(signal=sig)


if __name__ == '__main__':
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    baseline = pd.read_parquet(r'E:\SIDEPROJ\labwons-analytic\src\analysis\archive\baseline_sample.parquet', engine='pyarrow')
    strategy = Strategy(baseline)
    strategy.install()

    signal = strategy.drawdown_recover(describe=True)
    print(signal)