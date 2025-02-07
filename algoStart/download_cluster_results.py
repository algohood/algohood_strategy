# -*- coding: utf-8 -*-
"""
@Create: 2024/11/29 11:24
@File: download_cluster_results.py
@Author: Jingyuan
"""
import asyncio
from algoBroker.brokerMgr import BrokerMgr

loop = asyncio.get_event_loop()

task_id = '1737192506902110_target_test'
coro = BrokerMgr.download_results(task_id, 'target')
# coro = BrokerMgr.download_abstract(task_id, 'Performance', {'_fee_rate': 0})
# coro = BrokerMgr.download_abstract(task_id)
loop.run_until_complete(coro)
