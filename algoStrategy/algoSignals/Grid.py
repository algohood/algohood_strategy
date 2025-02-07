# -*- coding: utf-8 -*-
"""
@Create: 2024/10/17 8:51
@File: Grid.py
@Author: Jingyuan
"""
import uuid
from typing import Optional, List, Dict

from algoUtils.defUtil import SignalBase


class Algo(SignalBase):
    def __init__(self, _grid):
        self.grid = _grid
        self.last_price = None

    def generate_signals(self, _data: dict) -> Optional[List[Dict]]:
        signals = []
        for symbol, trades in _data.items():
            current_price = trades[-1][2]
            if self.last_price is None:
                self.last_price = current_price
                signals.append({
                    'batch_id': str(uuid.uuid4()),
                    'symbol': symbol,
                    'action': 'open',
                    'position': 'long',
                })

            if abs(current_price - self.last_price) / (current_price + self.last_price) * 2 <= self.grid:
                continue

            position = 'long' if current_price > self.last_price else 'short'
            self.last_price = current_price
            signals.append({
                'batch_id': str(uuid.uuid4()),
                'symbol': symbol,
                'action': 'open',
                'position': position,
            })

        return signals
