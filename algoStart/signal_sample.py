# -*- coding: utf-8 -*-
"""
@Create: 2024/10/17 8:51
@File: signal_sample.py
@Author: Jingyuan
"""
import asyncio

from algoBroker.brokerMgr import BrokerMgr
from algoUtils.dateUtil import local_datetime_timestamp
from algoUtils.schemaUtil import *


signal_mgr_param = SignalMgrParam(
    signal_method_name='Grid',
    signal_method_param={'_grid': 0.003},
    cool_down_ts=1,
)
    
feature_mgr_param = [
    # FeatureMgrParam(
    #     feature_method_name='PriceVolumeDivergence',
    #     feature_method_param={
    #         '_window_size': 60,
    #         '_epsilon': 1e-8,
    #     },
    # ),
    # FeatureMgrParam(
    #     feature_method_name='BuySellImbalance',
    #     feature_method_param={
    #         '_window_sec': 60,
    #     },
    # ),
    FeatureMgrParam(
        feature_method_name='MarketActivityPro',
        feature_method_param={
            '_batch_window': 600,
            '_vwap_epsilon': 1e-7,
            '_vola_window': 20,
            '_volume_trend_window': 30,
            '_buyer_power_window': 50,
            '_entropy_window': 100,
            '_impact_detection_quantile': 0.9,
            '_impact_effect_window': 10,
            '_fat_tail_window': 200,
            '_autocorr_lag': 3,
            '_micro_ratio_window': 50,
            '_reversal_threshold': 1.5,
            '_liquidity_ma_window': 5,
            '_cluster_interval_window': 20,
        },
    ),
]

target_mgr_param = TargetMgrParam(
    target_method_name='ReverseCounts',
    target_method_param={
        '_holding_period': 10,
        '_least_pct': 0.0001,
        '_intercept_threshold': 3,
    },
    target_fields='reverse_counts',
)

# model_mgr_param = ModelMgrParam(
#     model_method_name='SGDClassifier',
#     model_method_param={
#         '_learning_rate': 'optimal',
#         '_alpha': 1e-4,
#         '_epsilon': 1e-3,
#     },
#     model_cache_size=50,
#     model_retain_size=30,
# )

model_mgr_param = ModelMgrParam(
    model_method_name='RandomForestPredictor',
    model_method_param={
        '_n_estimators': 100,
        '_max_depth': 5,
        '_feature_stability_threshold': 0.85,
    },
    model_cache_size=50,
    model_retain_size=30,
)

# symbols = [
#     'doge_usdt|binance_future',
#     # 'sol_usdt|binance_future',
#     # 'xrp_usdt|binance_future',
#     # 'pnut_usdt|binance_future',
# ]
coro = BrokerMgr.get_active_symbols(_expire_duration=60 * 60 * 24 * 30, _data_type='trade')
symbols = asyncio.run(coro) or []

tasks = [
    SignalTaskParam(
        signal_task_name='grid_{}'.format(symbol).replace('|', '_'),
        signal_mgr_param=signal_mgr_param,
        feature_mgr_params=feature_mgr_param,
        # target_mgr_param=target_mgr_param,
        # model_mgr_param=model_mgr_param,
        lag=1,
        symbols=symbol,
        data_type='trade',
        start_timestamp=local_datetime_timestamp('2025-02-10 00:00:00'),
        end_timestamp=local_datetime_timestamp('2025-03-10 00:00:00'),
    )
    for symbol in symbols
]

coro = BrokerMgr.submit_signal_tasks(
    _task_name='grid',
    _tasks=tasks,
    _update_codes=True,
    _use_cluster=True
)

asyncio.run(coro)
