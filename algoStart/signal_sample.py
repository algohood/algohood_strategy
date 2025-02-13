# -*- coding: utf-8 -*-
"""
@Create: 2024/10/17 8:51
@File: signal_sample.py
@Author: Jingyuan
"""
import asyncio

from algoBroker.brokerMgr import BrokerMgr
from algoUtils.dateUtil import local_datetime_timestamp
from algoUtils.schemaUtil import SignalTaskParam, SignalMgrParam, FeatureMgrParam, TargetMgrParam, InterceptMgrParam


signal_mgr_param = SignalMgrParam(
    signal_method_name='Grid',
    signal_method_param={'_grid': 0.001},
)

feature_mgr_param = None
target_mgr_param = None
intercept_mgr_param = None
symbols = ['doge_usdt|binance_future']

tasks = [
    SignalTaskParam(
        signal_task_name='grid_{}'.format(symbol).replace('|', '_'),
        signal_mgr_param=signal_mgr_param,
        feature_mgr_params=feature_mgr_param,
        target_mgr_param=target_mgr_param,
        intercept_mgr_param=intercept_mgr_param,
        lag=0.1,
        symbols=symbol,
        data_type='trade',
        start_timestamp=local_datetime_timestamp('2025-02-01 00:00:00'),
        end_timestamp=local_datetime_timestamp('2025-02-02 00:00:00'),
    )
    for symbol in symbols
]

coro = BrokerMgr.submit_signal_tasks(
    _task_name='grid',
    _tasks=tasks,
    _update_codes=True,
    # _use_cluster=True
)

asyncio.run(coro)
