from datetime import datetime
from pandas import DataFrame


class Schema(DataFrame):

    __def__ = {
        'ticker': { 'index': True, 'dtype': str },
        'status': {'index': False, 'dtype': str},
        'detected_signal': {'index': False, 'dtype': str},
        'detected_time': {'index': False, 'dtype': datetime},
        'signal_confirmed_time': {'index': False, 'dtype': datetime},
        'bid_price': {'index': False, 'dtype': float},
        'execution_price': {'index': False, 'dtype': float},
        'yield': {'index': False, 'dtype': float},
        'executed_yield': {'index': False, 'dtype': float},
    }

    def __init__(self):
        super().__init__(
            DataFrame(
                index=list(self.__def__.keys()),
                data=self.__def__.values()
            ).T
        )
        return


if __name__ == "__main__":
    schema = Schema()
    print(schema)