from pandas import DataFrame
import pandas as pd


class Indicator:

    def __init__(self, baseline: DataFrame):
        self.data = baseline.copy()
        return

    def __call__(self, *tickers) -> DataFrame:
        return self.data.loc[:, pd.IndexSlice[list(tickers), :]]

    def __iter__(self):
        for col in self.data.columns.get_level_values(0).unique():
            yield col

    def __contains__(self, col: str):
        return col in self.data['KRW-BTC'].columns

    def __getitem__(self, col: str):
        return self.data.xs(col, axis=1, level=1)

    def __setitem__(self, col: str, series):
        series.columns = pd.MultiIndex.from_product([series.columns, [col]])
        self.data = pd.concat([self.data, series], axis=1).sort_index(axis=1)
        return

    def __delitem__(self, col: str):
        if not col in self:
            return
        mask = self.data.columns.get_level_values(1) == col
        self.data = self.data.drop(columns=self.data.columns[mask])
        return

    def _repr_html_(self):
        return self.data._repr_html_()

    def _set_columns(self, **kwargs):
        for column, series in kwargs.items():
            self[column] = series
        return

    def _del_columns(self, *cols):
        for col in cols:
            del self[col]
        return

    def install(self):
        self.add_tp()
        self.add_bb()
        self.add_macd()
        return

    def add_tp(self):
        self['tp'] = round((self['high'] + self['low'] + self['close']) / 3, 4)
        return

    def add_bb(self, basis: str = 'tp', window: int = 20, std: int = 2):
        basis = basis if basis in self else 'close'
        dev = self[basis].rolling(window).std()
        mid = self[basis].rolling(window).mean()
        up = mid + std * dev
        dn = mid - std * dev
        self._set_columns(
            mid=mid,
            bb_upper=up,
            bb_lower=dn,
            tr_upper=mid + (std / 2) * dev,
            tr_lower=mid - (std / 2) * dev,
            bb_width=((up - dn) / mid) * 100
        )
        return

    def add_macd(
        self,
        basis:str='tp',
        window_slow: int = 26,
        window_fast: int = 12,
        window_sign: int = 9,
    ):
        ema = lambda series, window: series.ewm(span=window).mean()
        fast = ema(self[basis], window_fast)
        slow = ema(self[basis], window_slow)
        macd = fast - slow
        sig = ema(macd, window_sign)
        self._set_columns(
            macd=macd,
            macd_signal=sig,
            macd_diff=macd - sig
        )
        return

# indicator = Indicator(coins.baseline)
# indicator.install()
# indicator.add_tp()
# indicator.add_bb()
# indicator

# indicator['amount']