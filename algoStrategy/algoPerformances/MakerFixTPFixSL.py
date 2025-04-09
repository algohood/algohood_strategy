from algoUtils.baseUtil import PerformanceBase
from algoUtils.schemaUtil import Signal, TradingResult
from typing import Optional, Dict
import numpy as np


class Algo(PerformanceBase):
    def __init__(self, _direction: int, _maker_bias: float, _maker_duration: float, _take_profit: float, _stop_loss: float):
        self.direction = _direction
        self.maker_bias = _maker_bias
        self.maker_duration = _maker_duration
        self.take_profit = _take_profit
        self.stop_loss = _stop_loss
        self.close_delay = 0.05
        self.signal_symbol = ''
        self.signal_timestamp = 0
        self.signal_price = 0
        self.cut_timestamp = 0

        self.maker_price = None
        self.profit_price = None
        self.stop_price = None
        self.entry_price = None
        self.entry_timestamp = None

    def init_signal(self, _signal: Signal):
        assert isinstance(_signal.price, float)
        assert isinstance(_signal.symbol, str)
        self.signal_symbol = _signal.symbol
        self.signal_timestamp = _signal.timestamp
        self.signal_price = abs(_signal.price)
        self.signal_direction = 1 if _signal.price > 0 else 0
        self.cut_timestamp = self.signal_timestamp + self.maker_duration

        multiplier = 1 if self.direction > 0 else -1
        self.maker_price = self.signal_price * (1 - multiplier * self.maker_bias)
        self.profit_price = self.maker_price * (1 + multiplier * self.take_profit)
        self.stop_price = self.maker_price * (1 - multiplier * self.stop_loss)

    def generate_trading_result(self, _data: Dict[str, np.ndarray]) -> Optional[TradingResult]:
        if self.direction * self.signal_direction < 0:
            return TradingResult(success=False)

        trades = _data[self.signal_symbol]
        if self.entry_price is None:
            condition_1 = trades[:, 1] > self.signal_timestamp
            condition_2 = trades[:, 1] < self.cut_timestamp
            condition_3 = trades[:, 2] < self.maker_price if self.direction > 0 else trades[:, 2] > self.maker_price

            filtered_trades = trades[condition_1 & condition_2 & condition_3]
            if filtered_trades.any():
                self.entry_price = self.maker_price
                self.entry_timestamp = filtered_trades[0, 1]

            elif trades[-1, 1] > self.cut_timestamp:
                return TradingResult(success=False)

            else:
                return

        if self.entry_price is not None and self.entry_timestamp is not None:
            condition_1 = trades[:, 1] > self.entry_timestamp + self.close_delay
            close_trades = trades[condition_1]
            if not close_trades.any():
                return

            condition_2 = close_trades[:, 2] > self.profit_price if self.direction > 0 else close_trades[:, 2] < self.profit_price
            condition_3 = close_trades[:, 2] < self.stop_price if self.direction > 0 else close_trades[:, 2] > self.stop_price

            filtered_trades = close_trades[condition_2 | condition_3]
            if filtered_trades.any():
                multiplier = 1 if self.direction > 0 else -1
                exit_price = filtered_trades[0, 2]
                exit_timestamp = filtered_trades[0, 1]
                trade_ret = (exit_price - self.entry_price) / self.entry_price * multiplier
                is_win = 1 if trade_ret > 0 else 0
                fee = 0.00018 if is_win else 0.00036
                trade_duration = exit_timestamp - self.entry_timestamp

                return TradingResult(
                    success=True,
                    direction=self.direction,
                    entry_timestamp=self.entry_timestamp,
                    exit_timestamp=exit_timestamp,
                    is_win=is_win,
                    trade_ret=trade_ret - fee,
                    trade_duration=trade_duration,
                )

