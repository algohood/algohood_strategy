# -*- coding: utf-8 -*-
"""
@Create on  2025/1/21 19:13
@file: init_redis.py
@author: Jerry
"""
from algoBroker.brokerMgr import BrokerMgr
from algoUtils.loggerUtil import generate_logger
from algoConfig.redisConfig import redis_host, config_port, node_port

logger = generate_logger()

redis_host = BrokerMgr.get_wsl_ip()  # u could set ur redis host here!

# download data from binance data server
# symbols = 'doge_usdt'  # this could be a list of symbols like ['btc_usdt', 'eth_usdt']
symbols = ['doge_usdt', 'sol_usdt', 'xrp_usdt', 'pnut_usdt']  # this could be a list of symbols like ['btc_usdt', 'eth_usdt']
start_dt = '2025-01-01'
end_dt = '2025-02-01'

BrokerMgr.download_trades(symbols, start_dt, end_dt)

# sync data from folder to redis
BrokerMgr.sync_redis(symbols, redis_host, config_port, node_port)
