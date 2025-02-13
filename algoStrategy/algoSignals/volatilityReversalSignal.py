import numpy as np
from typing import Dict, List, Optional
from algoUtils.defUtil import SignalBase
from algoUtils.schemaUtil import Signal
from collections import deque
import uuid

class Algo(SignalBase):
    """
    实现瞬时波动检测与反转信号触发的算法类。

    该算法通过以下步骤进行信号生成：
    1. 计算给定时间窗口内的价格变化幅度（最高价与最低价之差）。
    2. 维护历史价格变化幅度的列表，并计算其平均值。
    3. 如果当前价格变化幅度超过历史平均值的指定倍数，判断为瞬时波动。
    4. 在瞬时波动发生后，监控价格是否向相反方向移动，如果变化幅度超过指定阈值，则触发反转信号。

    :param _time_window: 时间窗口长度（秒），用于计算价格变化幅度。
    :param _volatility_threshold_multiplier: 波动阈值倍数，用于判断瞬时波动。
    :param _reversal_threshold: 反转信号触发阈值，价格变化幅度超过该值时触发信号。
    """

    def __init__(self, _time_window: float = 1.0, _volatility_threshold_multiplier: float = 2.0, _reversal_threshold: float = 0.01):
        self.time_window = _time_window
        self.volatility_threshold_multiplier = _volatility_threshold_multiplier
        self.reversal_threshold = _reversal_threshold
        self.price_history = deque()
        self.volatility_history = deque()
        self.volatility_threshold = None
        self.instantaneous_volatility_detected = False
        self.last_volatility_end_price = None

    def generate_signals(self, _data: Dict[str, List[List]]) -> Optional[List[Signal]]:
        """
        生成交易信号的入口方法。

        :param _data: 包含各交易对最新市场数据的字典，key为交易对符号，value为最新tick数据列表。
        :return: 如果有交易信号，返回信号列表；否则返回None。
        """
        signals = []
        for symbol, ticks in _data.items():
            for tick in ticks:
                recv_ts, _, price, _, _ = tick
                self.price_history.append((recv_ts, price))

                # 移除超出时间窗口的历史价格数据
                while self.price_history and recv_ts - self.price_history[0][0] > self.time_window:
                    self.price_history.popleft()

                if len(self.price_history) > 1:
                    prices = np.array([p for _, p in self.price_history])
                    price_range = np.max(prices) - np.min(prices)
                    self.volatility_history.append(price_range)

                    # 计算历史波动幅度的平均值
                    if len(self.volatility_history) > 10:  # 使用最近10个数据点计算平均值
                        avg_volatility = np.mean(list(self.volatility_history)[-10:])
                        self.volatility_threshold = avg_volatility * self.volatility_threshold_multiplier

                        # 检测瞬时波动
                        if price_range > self.volatility_threshold:
                            self.instantaneous_volatility_detected = True
                            self.last_volatility_end_price = prices[-1]

                    # 检测反转信号
                    if self.instantaneous_volatility_detected and price != self.last_volatility_end_price:
                        price_change = abs(price - self.last_volatility_end_price) / self.last_volatility_end_price
                        if price_change > self.reversal_threshold:
                            action = 'close' if price > self.last_volatility_end_price else 'open'
                            position = 'long' if price < self.last_volatility_end_price else 'short'
                            signals.append(Signal(
                                batch_id=str(uuid.uuid4()),
                                symbol=symbol,
                                action=action,
                                position=position
                            ))
                            self.instantaneous_volatility_detected = False
        return signals if signals else None