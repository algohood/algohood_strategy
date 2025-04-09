import asyncio
from algoBroker.brokerMgr import BrokerMgr
from algoUtils.schemaUtil import *


tasks = [
    PerformanceMgrParam(
        performance_name='MakerFixTPFixSL',
        performance_method_name='MakerFixTPFixSL',
        performance_method_param={
            '_direction': 0,
            '_maker_bias': 0.0001,
            '_maker_duration': 10,
            '_take_profit': 0.003,
            '_stop_loss': 0.002,
        },
    )
]

signal_task_id = '1744161521126849_grid'
coro = BrokerMgr.submit_performance_tasks(
    _task_name='MakerFixTPFixSL',
    _tasks=tasks,
    _signal_task_name=signal_task_id,
    _update_codes=True,
    # _use_cluster=True,
)

asyncio.run(coro)
