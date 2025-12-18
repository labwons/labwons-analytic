from pandas import DataFrame
import pandas as pd
import os


class Tracker(object):

    if '__file__' in globals():
        root = os.path.dirname(__file__)
    else:
        root = os.getcwd()
    archive = os.path.join(root, 'archive')
    os.makedirs(archive, exist_ok=True)

    def __init__(self, file:str=''):
        self._src = file
        self.data = self._init(file)
        return

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value
    #
    # def __getattr__(self, item):
    #     try:
    #         return getattr(self.data, item)
    #     except AttributeError:
    #         return super().__getattribute__(item)

    def __repr__(self):
        return repr(self.data)

    def __str__(self):
        return str(self.data)

    def _repr_html_(self):
        return getattr(self.data, '_repr_html_')()

    @classmethod
    def _init(cls, file:str='') -> DataFrame:
        if not file:
            return DataFrame()
        if not file.endswith('.parquet'):
            file = f'{file}.parquet'
        src = os.path.join(cls.archive, file)
        if not os.path.exists(src):
            return DataFrame()
        return pd.read_parquet(src, engine='pyarrow')

    @property
    def file(self) -> str:
        return self._src

    @file.setter
    def file(self, file:str):
        self.data = self._init(file)

    def add_row(self, row):
        return

    def close(self):
        self.save()

    def save(self):
        self.data.to_parquet(self.file, engine='pyarrow')



if __name__ == '__main__':
    from pandas import set_option
    set_option('display.expand_frame_repr', False)

    # Tracker.archive = r'C:\Users\Administrator\Downloads'
    tracker = Tracker('signal')
    print(tracker)

    # df = pd.read_json(r'E:\SIDEPROJ\labwons-analytic\src\bot\book\book.json', orient='index') \
    #        .set_index(keys='ticker')
    # df = df[[
    #     'signal',
    #     'signaled_time',
    #     'signaled_price',
    #     'signaled_amount',
    #     'signaled_volume'
    # ]]
    # df.columns = ['signal', 'datetime', 'price', 'amount', 'volume']
    # df['interval'] = '60minutes'
    # df = df[['signal', 'datetime', 'interval', 'price', 'amount', 'volume']]
    # df.to_parquet(r'E:\SIDEPROJ\labwons-analytic\src\analysis\archive\signal.parquet', engine='pyarrow')
    # print(df)
