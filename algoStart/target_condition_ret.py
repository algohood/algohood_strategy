# -*- coding: utf-8 -*-
"""
@Create on  2024/9/29 16:22
@file: target_condition_ret.py
@author: Jerry
"""
import asyncio
from algoBroker.brokerMgr import BrokerMgr

loop = asyncio.get_event_loop()

file = BrokerMgr.get_abstract_given_file_name('1737187389799932_slow_grids').to_dict('records')
# signal_paths = [v['result_path'] for v in file if 'grid_w_usdt' in v['_signal_name']]
signal_paths = [v['result_path'] for v in file]

tasks = [
    BrokerMgr.prepare_target_task(
        _target_name='maker_condition_ret_{}'.format(stop_delay),
        _target_method_name='MakerConditionRet',
        _target_method_param={
            '_maker_hold': 10,
            '_profit_grid': 0.0011,
            '_stop_grid': 0.0009,
            '_stop_delay': stop_delay
        },
        _data_type='trade',
    )
    for stop_delay in range(0, 60, 5)
]

coro = BrokerMgr.submit_target_tasks(
    _task_name='target_test',
    _tasks=tasks,
    _signal_paths=signal_paths,
    _keep_empty=False,
    _abstract_method='Performance',
    _abstract_param={'_fee_rate': 0},
    _update_codes=True,
    _use_cluster=True
)
loop.run_until_complete(coro)
