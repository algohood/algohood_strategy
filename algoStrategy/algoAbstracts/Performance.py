# -*- coding: utf-8 -*-
"""
@Create: 2025/1/16 20:08
@File: Performance.py
@Author: Jingyuan
"""
import numpy as np
from typing import Optional, Dict

from algoUtils.defUtil import AbstractBase


class Algo(AbstractBase):
    def __init__(self, _fee_rate):
        self.fee_rate = _fee_rate

    def generate_abstract(self, _targets: list) -> Optional[Dict]:
        long_info = {}
        short_info = {}
        abstract = {'total_amount': 0}
        for target in _targets:
            a_m = 1 if target['action'] == 'open' else -1
            p_m = 1 if target['position'] == 'long' else -1
            ret = target['target_ret'] - self.fee_rate
            if a_m * p_m > 0:
                long_info.setdefault('win', []).append(target['target_win'])
                key = 'win_ret' if target['target_win'] > 0 else 'loss_ret'
                long_info.setdefault(key, []).append(ret)
                long_info.setdefault('ret', []).append(ret)
            else:
                short_info.setdefault('win', []).append(target['target_win'])
                key = 'win_ret' if target['target_win'] > 0 else 'loss_ret'
                short_info.setdefault(key, []).append(ret)
                short_info.setdefault('ret', []).append(ret)

        if long_info:
            win_ret = long_info.get('win_ret')
            loss_ret = long_info.get('loss_ret')
            abstract.update({
                'long_win': float(np.mean(long_info['win'])),
                'long_ret': sum(long_info['ret']),
                'long_win_avg_ret': float(np.mean(win_ret)) if win_ret else None,
                'long_loss_avg_ret': float(np.mean(loss_ret)) if loss_ret else None,
            })

        if short_info:
            win_ret = short_info.get('win_ret')
            loss_ret = short_info.get('loss_ret')
            abstract.update({
                'short_win': float(np.mean(short_info['win'])),
                'short_ret': sum(short_info['ret']),
                'short_win_avg_ret': float(np.mean(win_ret)) if win_ret else None,
                'short_loss_avg_ret': float(np.mean(loss_ret)) if loss_ret else None,
            })

        return abstract
