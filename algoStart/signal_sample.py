import asyncio

from algoBroker.brokerMgr import BrokerMgr
from algoAgent.models import *
from algoUtils.dateUtil import local_datetime_timestamp

symbols = ['doge_usdt|binance_future']
tasks = [
    BrokerMgr.prepare_signal_task(
        _signal_name='macd_{}'.format(symbol).replace('|', '_'),
        _signal_method_name='macdCrossSignal',
        _signal_method_param={
            '_fast_period': 12, 
            '_slow_period': 26, 
            '_signal_period': 9
        },
        _intercept_method_name='volatilityMetrics',
        _intercept_method_param={
            # 核心参数
            '_window_sec': 600,          # 分析窗口时长（秒）覆盖快慢线周期总和
            '_tick_threshold': 200,      # 最小有效tick数（约2倍快线周期）
            '_atr_window': 20,           # ATR窗口（快慢线周期平均值）
            
            # 波动特征参数
            '_vol_cluster_window': 30,    # 波动聚集检测窗口
            '_price_change_window': 12,   # 价格变化率窗口（对齐快线周期）
            '_instant_vol_window': 5,     # 瞬时波动窗口（高频检测）
            
            # 趋势参数
            '_trend_min_ticks': 3,        # 趋势计算最小tick数
            '_skewness_window': 26,       # 偏度窗口（对齐慢线周期）
            
            # 风险控制
            '_dd_threshold': 0.001,        # 回撤阈值（3%）
            '_delay_sec': 5,             # 延迟监测时间（秒）
            
            # 机器学习参数
            '_train_window': 200,         # 训练数据窗口
            '_lr': 0.005,                 # 学习率（保守更新）
            '_reg_lambda': 0.2,           # 正则化强度
            
            # 拦截机制
            '_intercept_threshold': 0.58, # 动态胜率阈值
            '_cool_down_sec': 150         # 冷却时间（秒）
        },
        _data_type='trade',
        _symbols=symbol,
        _lag=60,
        _start_timestamp=local_datetime_timestamp('2025-01-21 00:00:00'),
        _end_timestamp=local_datetime_timestamp('2025-02-06 00:00:00'),
    )
    for symbol in symbols
]

coro = BrokerMgr.submit_signal_tasks(
    _task_name='signal_sample',
    _tasks=tasks,
    _update_codes=True,
    _use_cluster=False
)

asyncio.run(coro)
