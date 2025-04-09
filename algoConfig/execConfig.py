# -*- coding: utf-8 -*-
"""
@Create: 2024/11/30 12:06
@File: execConfig.py
@Author: Jingyuan
"""
delay_dict = {
    'binance_future': {
        '_send_delay': 0.01,
        '_cancel_back': 0.005,
        '_execute_back': 0.01
    },

    'binance_spot': {
        '_send_delay': 0.015,
        '_cancel_back': 0.005,
        '_execute_back': 0.018
    }
}

fee_dict = {
    'binance_future': {
        '_maker_fee': 0.0001,
        '_taker_fee': 0.00027
    },

    'binance_spot': {
        '_maker_fee': 0.000315,
        '_taker_fee': 0.000405
    }
}
