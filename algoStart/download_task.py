from algoBroker.brokerMgr import BrokerMgr
import asyncio

task_id = '1743153839062941_MakerFixTPFixSL'
asyncio.run(BrokerMgr.download_abstract(task_id))
