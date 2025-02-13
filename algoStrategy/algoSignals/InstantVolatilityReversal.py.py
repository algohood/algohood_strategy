from algoUtils.baseUtil import SignalBase
from algoUtils.schemaUtil import Signal
from typing import Dict, List, Optional
import numpy as np
import uuid

class Algo(SignalBase):
    """
    基于瞬时波动反转信号的策略类。

    参数:
    - _lookback_period: int, 计算瞬时波动的回溯笔数。
    - _reversal_threshold: float, 触发反转信号的波动阈值。
    - _confirmation_period: int, 信号确认的成交笔数。
    """
    def __init__(self, _lookback_period: int, _reversal_threshold: float, _confirmation_period: int):
        self.lookback_period = _lookback_period
        self.reversal_threshold = _reversal_threshold
        self.confirmation_period = _confirmation_period
        self.symbol_buffer = {}  # 用于存储各 symbol 的历史数据

    def generate_signals(self, _data: Dict[str, List[List]]) -> Optional[List[Signal]]:
        """
        生成交易信号的函数。

        参数:
        - _data: Dict[str, List[List]], 包含各 symbol 的历史成交数据。

        返回:
        - Optional[List[Signal]]: 生成的交易信号列表，若无有效信号则返回 None。
        """
        signals = []
        for symbol, ticks in _data.items():
            if symbol not in self.symbol_buffer:
                self.symbol_buffer[symbol] = []

            # 更新缓冲区
            self.symbol_buffer[symbol].extend(ticks)

            # 检查是否有足够数据
            if len(self.symbol_buffer[symbol]) < self.lookback_period + self.confirmation_period:
                continue

            # 提取价格数据
            prices = np.array([tick[2] for tick in self.symbol_buffer[symbol]])

            # 计算瞬时波动
            current_price = prices[-1]
            past_price = prices[-(self.lookback_period + 1)]
            price_change = (current_price - past_price) / past_price * 100

            # 判断是否触发反转信号
            if abs(price_change) > self.reversal_threshold:
                # 确定信号方向
                action = "open"
                position = "short" if price_change > 0 else "long"

                # 信号确认
                future_prices = prices[-self.confirmation_period:]
                if position == "short" and np.all(np.diff(future_prices) <= 0):
                    signals.append(Signal(
                        batch_id=str(uuid.uuid4()),
                        symbol=symbol,
                        action=action,
                        position=position
                    ))
                elif position == "long" and np.all(np.diff(future_prices) >= 0):
                    signals.append(Signal(
                        batch_id=str(uuid.uuid4()),
                        symbol=symbol,
                        action=action,
                        position=position
                    ))

            # 清理缓冲区，避免内存溢出
            if len(self.symbol_buffer[symbol]) > (self.lookback_period + self.confirmation_period) * 10:
                self.symbol_buffer[symbol] = self.symbol_buffer[symbol][-(self.lookback_period + self.confirmation_period):]

        return signals if signals else None