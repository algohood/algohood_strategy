# -*- coding: utf-8 -*-
"""
@Create: 2024/10/17 8:51
@File: Grid.py
@Author: Jingyuan
"""
import uuid
from typing import Optional, List, Dict

from algoUtils.baseUtil import SignalBase
from algoUtils.baseUtil import Signal


class Algo(SignalBase):
    def __init__(self, _grid):
        self.grid = _grid
        self.last_price = None

    def update_state(self, _current_ts: float, _data: dict):
        pass

    def generate_signals(self, _current_ts: float, _data: dict) -> Optional[Signal]:
        symbol, trades = next(iter(_data.items()))
        current_price = trades[-1, 2]
        if self.last_price is None:
            self.last_price = current_price
            return

        if abs(current_price - self.last_price) / (current_price + self.last_price) * 2 <= self.grid:
            return

        multiplier = 1 if current_price > self.last_price else -1
        self.last_price = current_price

        return Signal(
            batch_id=str(uuid.uuid4()),
            symbol=symbol,
            price=current_price * multiplier,
        )
