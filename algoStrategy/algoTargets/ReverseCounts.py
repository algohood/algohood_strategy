from algoUtils.baseUtil import TargetBase
from algoUtils.schemaUtil import Signal
from typing import Dict, Optional
import math
import numpy as np


class Algo(TargetBase):
    def __init__(self, _holding_period: int, _least_pct: float, _intercept_threshold: int):
        self.holding_period = _holding_period
        self.least_pct = _least_pct
        self.intercept_threshold = _intercept_threshold
        self.cut_timestamp = 0
        self.start_price = 0
        self.direction = None
        self.cache_data = []

    def init_instance(self, _signal: Signal):
        assert isinstance(_signal.price, float)
        self.cut_timestamp = _signal.timestamp + self.holding_period
        self.start_price = abs(_signal.price)
        self.direction = 1 if _signal.price > 0 else -1

    def generate_targets(self, _current_ts: float, _data: Dict[str, np.ndarray]) -> Optional[Dict[str, float]]:
        _, batch_data = next(iter(_data.items()))
        if not batch_data.any():
            return

        if _current_ts < self.cut_timestamp:
            self.cache_data.extend(batch_data[:, 2])
            return

        if not self.cache_data:
            return {'reverse_counts': 0, 'bias': 0}

        avg_close = np.mean(self.cache_data)
        bias = (avg_close - self.start_price) / self.start_price
        last_position = None
        reverse_counts = 0
        for trade in self.cache_data:
            if last_position is None:
                if trade > avg_close * (1 + self.least_pct):
                    last_position = 1
                elif trade < avg_close * (1 - self.least_pct):
                    last_position = -1
            else:
                if trade > avg_close * (1 + self.least_pct):
                    current_position = 1
                elif trade < avg_close * (1 - self.least_pct):
                    current_position = -1
                else:
                    current_position = last_position

                if current_position * last_position < 0:
                    reverse_counts += 1
                    last_position = current_position

        return {'reverse_counts': float(math.log(reverse_counts + 1)), 'bias': float(bias)}

    def intercept_signal_given_targets(self, _targets: Dict[str, float]) -> bool:
        return _targets['reverse_counts'] < float(math.log(self.intercept_threshold + 1))
