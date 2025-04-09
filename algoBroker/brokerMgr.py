# -*- coding: utf-8 -*-
"""
@Create: 2024/9/30 14:06
@File: brokerMgr.py
@Author: Jingyuan
"""
import asyncio
import gzip
import importlib
import inspect
import json
import os
import subprocess
import time
import zipfile
from typing import List
import pandas as pd
import requests

from algoConfig.zmqConfig import zmq_host, zmq_port
from algoConfig.redisConfig import redis_host, config_port, is_localhost

from algoSignal.algoEngine.dataMgr import DataMgr as SignalDataMgr
from algoSignal.algoEngine.eventMgr import EventMgr as SignalEventMgr
from algoSignal.algoEngine.signalMgr import SignalMgr
from algoSignal.algoEngine.modelMgr import ModelMgr
from algoSignal.algoEngine.targetMgr import TargetMgr
from algoSignal.algoEngine.featureMgr import FeatureMgr
from algoSignal.algoEngine.performanceMgr import PerformanceMgr

from algoUtils.asyncRedisUtil import AsyncRedisClient
from algoUtils.schemaUtil import SignalTaskParam, PerformanceMgrParam, Signal
from algoUtils.asyncZmqUtil import AsyncReqZmq
from algoUtils.dateUtil import date_list_given_start_end, local_date_timestamp
from algoUtils.loggerUtil import generate_logger

logger = generate_logger(level='DEBUG')


class BrokerMgr:

    @staticmethod
    def get_abstract_given_file_name(_file_name):
        try:
            file = pd.read_csv('../algoFile/abstract_{}.csv'.format(_file_name))
            return file
        except Exception as e:
            logger.error(e)

    @staticmethod
    async def get_active_symbols(_expire_duration, _data_type):
        zmq_client = AsyncReqZmq(zmq_port, zmq_host)
        task_dict = {
            'task_type': 'active_symbols', 'task': {'expire_duration': _expire_duration, 'data_type': _data_type}
        }
        tmp = await zmq_client.send_msg(json.dumps(task_dict).encode())
        if tmp is None:
            return

        rsp = json.loads(tmp.decode())
        if rsp['code'] == 200:
            return rsp['msg']

        else:
            logger.error(rsp['msg'])

    @classmethod
    async def submit_signal_tasks(
        cls, _task_name: str, _tasks: List[SignalTaskParam], _update_codes=True, _use_cluster=False
    ):
        signal_task_names = [v.signal_task_name for v in _tasks]
        if len(signal_task_names) > len(set(signal_task_names)):
            logger.error('duplicated signal task names')
            return

        if _use_cluster:
            zmq_client = AsyncReqZmq(zmq_port, zmq_host)
            module_names_dict = {}
            for task in _tasks:
                module_names_dict.setdefault('Signals', set()).add(task.signal_mgr_param.signal_method_name)
                
                if task.target_mgr_param:
                    module_names_dict.setdefault('Targets', set()).add(task.target_mgr_param.target_method_name)
                
                if task.model_mgr_param:
                    module_names_dict.setdefault('Models', set()).add(task.model_mgr_param.model_method_name)
                
                if isinstance(task.feature_mgr_params, list):
                    for feature_mgr_param in task.feature_mgr_params:
                        module_names_dict.setdefault('Features', set()).add(feature_mgr_param.feature_method_name)

                elif task.feature_mgr_params:
                    module_names_dict.setdefault('Features', set()).add(task.feature_mgr_params.feature_method_name)

            for module_type, module_names in module_names_dict.items():
                for name in module_names:
                    module = importlib.import_module('algoStrategy.algo{}.{}'.format(module_type, name))
                    script_content = inspect.getsource(module) if _update_codes else ''

                task_dict = {'task_type': 'signal', 'task': {'type': 'code', 'info': {
                    'module_name': name, 'module_type': module_type, 'scripts': script_content
                }}}
                tmp = await zmq_client.send_msg(json.dumps(task_dict).encode())
                if tmp is None:
                    logger.error('failed to submit signal tasks')
                    return

                rsp = json.loads(tmp.decode())
                if rsp['msg'] != 'finished':
                    logger.error(rsp['msg'])
                    return

            logger.info('strategy checked')
            task_dict = {
                'task_type': 'signal', 
                'task': {
                    'task_name': _task_name, 
                    'type': 'tasks', 
                    'info': [task.model_dump() for task in _tasks]
                }
            }
            tmp = await zmq_client.send_msg(json.dumps(task_dict).encode())
            if tmp is None:
                logger.error('failed to submit signal tasks')
                return

            rsp = json.loads(tmp.decode())
            if rsp['code'] == 200:
                logger.info('{} tasks submitted'.format(rsp['msg']))
                await cls.download_abstract(rsp['msg'])
            else:
                logger.error(rsp['msg'])

        else:
            file_name = '{}_{}'.format(int(time.time() * 1000000), _task_name)

            data_mgr = SignalDataMgr(redis_host, config_port)
            await data_mgr.init_data_mgr(is_localhost)
            abstract_list = []
            for task in _tasks:
                data_mgr.clear_cache()
                result_path = '{}/{}'.format(file_name, task.signal_task_name)
                data_mgr.set_data_type(task.data_type)

                # init mgrs
                signal_mgr = SignalMgr(task.signal_mgr_param)
                feature_mgr = FeatureMgr(task.feature_mgr_params)
                model_mgr = ModelMgr(task.model_mgr_param)
                target_mgr = TargetMgr(task.target_mgr_param)

                event_mgr = SignalEventMgr(
                    signal_mgr,
                    feature_mgr,
                    target_mgr,
                    model_mgr,
                    data_mgr,
                )

                signals = await event_mgr.start_task(
                    task.lag,
                    task.symbols,
                    task.start_timestamp,
                    task.end_timestamp,
                )

                if signals:
                    abstract = {'result_path': result_path, 'result_counts': len(signals)}
                    os.makedirs('../algoFile/{}'.format(file_name), exist_ok=True)
                    abstract_list.append({**abstract, **task.model_dump(exclude_defaults=True)})
                    pd.DataFrame(signals).to_csv('../algoFile/{}.csv'.format(result_path))
                    logger.info('{} finished'.format(task.signal_task_name))

            if abstract_list:
                pd.DataFrame(abstract_list).to_csv('../algoFile/abstract_{}.csv'.format(file_name))

            logger.info('{} finished'.format(file_name))

    @classmethod
    async def submit_performance_tasks(
            cls, _task_name, _tasks, _signal_task_name, _update_codes=True, _use_cluster=False
    ):
        performance_names = [v.performance_name for v in _tasks]
        if len(performance_names) > len(set(performance_names)):
            logger.error('duplicated performance names')
            return
        
        abstracts = pd.read_csv('../algoFile/abstract_{}.csv'.format(_signal_task_name)).to_dict('records')
        if not abstracts:
            logger.error('signal abstract does not exist')
            return

        if _use_cluster:
            zmq_client = AsyncReqZmq(zmq_port, zmq_host)
            module_names = set([v.performance_method_name for v in _tasks])

            for name in module_names:
                module_name = 'algoStrategy.algoPerformances.{}'.format(name)
                module = importlib.import_module(module_name)
                script_content = inspect.getsource(module) if _update_codes else ''

                task_dict = {'task_type': 'performance', 'task': {'type': 'code', 'info': {
                    'module_name': name, 'scripts': script_content
                }}}
                tmp = await zmq_client.send_msg(json.dumps(task_dict).encode())
                if tmp is None:
                    logger.error('failed to submit performance tasks')
                    return

                rsp = json.loads(tmp.decode())
                if rsp['msg'] != 'finished':
                    logger.error(rsp['msg'])
                    return

            task_dict = {'task_type': 'performance', 'task': {
                'type': 'tasks',
                'task_name': _task_name,
                'abstracts': abstracts,
                'info': [task.model_dump() for task in _tasks],
            }}

            tmp = await zmq_client.send_msg(json.dumps(task_dict).encode())
            if tmp is None:
                logger.error('failed to submit performance tasks')
                return

            rsp = json.loads(tmp.decode())
            if rsp['code'] == 200:
                logger.info('{} tasks submitted'.format(rsp['msg']))
                await cls.download_abstract(rsp['msg'])
            else:
                logger.error(rsp['msg'])

        else:
            file_name = '{}_{}'.format(int(time.time() * 1000000), _task_name)

            data_mgr = SignalDataMgr(redis_host, config_port)
            await data_mgr.init_data_mgr(is_localhost)

            tasks = [_tasks] if isinstance(_tasks, PerformanceMgrParam) else _tasks
            performance_abstracts = []
            for task in tasks:
                for abstract in abstracts:
                    _, signal_name = abstract['result_path'].split('/')
                    file_path = '../algoFile/{}.csv'.format(abstract['result_path'])
                    signals_list = pd.read_csv(file_path).to_dict('records')
                    if not signals_list:
                        logger.error('signal does not exist: {}'.format(abstract['result_path']))
                        continue

                    signals = []
                    for signal in signals_list:
                        signal.pop('Unnamed: 0', None)
                        signals.append(Signal(
                            batch_id=signal.pop('batch_id'),
                            symbol=signal.pop('symbol'),
                            timestamp=signal.pop('timestamp'),
                            price=signal.pop('price'),
                            other_info=signal,
                        ))

                    data_mgr.clear_cache()
                    data_mgr.set_data_type(abstract['data_type'])
                    performance_mgr = PerformanceMgr(task, data_mgr)
                    performance_mgr.init_signals(
                        _symbols=abstract['symbols'],
                        _start_timestamp=abstract['start_timestamp'],
                        _end_timestamp=abstract['end_timestamp'],
                        _signals=signals,
                    )
                    performance_list, performance_abstract = await performance_mgr.start_task()

                    task_path = '../algoFile/{}/{}'.format(file_name, task.performance_name)
                    performance_abstracts.append({
                        'result_path': '{}/{}/{}'.format(file_name, task.performance_name, signal_name),
                        'signal_counts': len(signals),
                        'result_counts': len(performance_list),
                        **task.model_dump(exclude_defaults=True),
                        **performance_abstract,
                    })

                    if performance_list:
                        os.makedirs(task_path, exist_ok=True)
                        pd.DataFrame(performance_list).to_csv('{}/{}.csv'.format(task_path, signal_name))
                        logger.info('{}/{} finished'.format(task.performance_name, signal_name))

            if performance_abstracts:
                pd.DataFrame(performance_abstracts).to_csv('../algoFile/abstract_{}.csv'.format(file_name))

            logger.info('{} finished'.format(file_name))

    @classmethod
    async def download_results(cls, _task_id, _task_type, _split=True):
        check_list = ['signal', 'performance', 'exec', 'portfolio']
        if _task_type not in check_list:
            logger.error('unknown task type: {}|{}'.format(_task_type, check_list))
            return

        zmq_client = AsyncReqZmq(zmq_port, zmq_host)
        abstract_list = pd.read_csv('../algoFile/abstract_{}.csv'.format(_task_id)).to_dict('records')
        if not abstract_list:
            logger.error('abstract does not exist')
            return

        for abstract in abstract_list:
            try:
                task_dict = {'task_type': 'download_results', 'task': {
                    'result_path': abstract['result_path'], 'result_type': _task_type
                }}
                tmp = await zmq_client.send_msg(json.dumps(task_dict).encode())
                if tmp is None:
                    logger.error('failed to download results')
                    return

                decompressed = gzip.decompress(tmp)
                rsp = json.loads(decompressed.decode())
                if rsp['code'] == 250:
                    logger.error(rsp['msg'])
                    continue

                if rsp['msg']:
                    if _task_type == 'exec':
                        file_path = '../algoFile/{}/{}'.format(_task_id, abstract['_execute_name'])
                        os.makedirs(file_path, exist_ok=True)
                        pd.DataFrame(rsp['msg']).to_csv('{}/{}.csv'.format(file_path, abstract['signal_name']))
                        logger.info('{} finished: {}'.format(
                            abstract['result_path'], len(rsp['msg'])
                        ))

                    elif _task_type == 'signal':
                        os.makedirs('../algoFile/{}'.format(_task_id), exist_ok=True)
                        pd.DataFrame(rsp['msg']).to_csv('../algoFile/{}.csv'.format(abstract['result_path']))
                        logger.info('{} finished: {}'.format(
                            abstract['result_path'], len(rsp['msg'])
                        ))

                    elif _task_type == 'performance':
                        os.makedirs('../algoFile/{}/{}'.format(_task_id, abstract['_performance_name']), exist_ok=True)
                        pd.DataFrame(rsp['msg']).to_csv('../algoFile/{}.csv'.format(abstract['result_path']))
                        logger.info('{} finished: {}'.format(
                            abstract['result_path'], len(rsp['msg'])
                        ))

                    elif _task_type == 'portfolio':
                        file_path = '../algoFile/cluster_{}/{}'.format(_task_id, abstract['portfolio_name'])
                        os.makedirs(file_path, exist_ok=True)
                        pd.DataFrame(rsp['msg']).to_csv('{}/{}.csv'.format(file_path, abstract['order_name']))
                        logger.info('{}/{} finished: {}'.format(
                            abstract['portfolio_name'], abstract['order_name'], len(rsp['msg'])
                        ))

            except Exception as e:
                logger.error(e)
                time.sleep(60)

    @classmethod
    async def download_abstract(cls, _task_id):
        zmq_client = AsyncReqZmq(zmq_port, zmq_host)
        if not await cls.check_left(zmq_client, _task_id):
            return

        # download abstract
        task_dict = {'task_type': 'download_abstract', 'task': {'task_id': _task_id}}
        tmp = await zmq_client.send_msg(json.dumps(task_dict).encode())
        if tmp is None:
            logger.error('failed to download abstract')
            return

        rsp = json.loads(tmp.decode())
        if rsp['code'] == 200:
            pd.DataFrame(rsp['msg']).to_csv('../algoFile/abstract_{}.csv'.format(_task_id))
            logger.info('{} abstract saved'.format(_task_id))

        else:
            logger.info('{} not available: {}'.format(_task_id, rsp['msg']))

    @classmethod
    async def check_left(cls, _zmq_client, _task_id) -> bool:
        while True:
            try:
                msg = json.dumps({'task_type': 'check', 'task': _task_id}).encode()
                tmp = await _zmq_client.send_msg(msg)
                rsp = json.loads(tmp.decode())
                if rsp['code'] == 200:
                    if rsp['msg'] is None:
                        logger.info('{} finished'.format(_task_id))
                        return True

                    logger.info('{} left {}'.format(_task_id, rsp['msg']))
                    await asyncio.sleep(5)

                else:
                    logger.error(rsp['msg'])
                    return False

            except Exception as e:
                logger.error(e)
                time.sleep(60)

    @classmethod
    def download_trades(cls, _symbols, _start_dt, _end_dt):
        symbols = _symbols if isinstance(_symbols, list) else [_symbols]
        date_list = date_list_given_start_end(_start_dt, _end_dt)

        folder_path = '../algoData'
        os.makedirs(folder_path, exist_ok=True)
        file_list = os.listdir(folder_path)
        for symbol in symbols:
            for date_str in date_list:
                tmp = symbol.replace('_', '').upper()
                url_path = 'https://data.binance.vision/data/futures/um/daily/aggTrades/{}'.format(tmp)
                check_name = '{}-aggTrades-{}.zip'.format(symbol, date_str)
                if check_name in file_list:
                    logger.info('{} already exist'.format(check_name))
                    continue

                download_url = '{}/{}-aggTrades-{}.zip'.format(url_path, tmp, date_str)
                save_path = '{}/{}'.format(folder_path, check_name)

                try:
                    with requests.get(download_url, stream=True) as dl_file:
                        # 检查响应的状态码
                        if dl_file.status_code != 200:
                            print(f"Failed to download file: HTTP {dl_file.status_code}")
                            return

                        # 获取文件大小（如果提供）
                        length = dl_file.headers.get('Content-Length')
                        if length:
                            length = int(length)
                            blocksize = max(4096, length // 9)
                        else:
                            blocksize = 4096  # 如果没有提供文件大小，则默认为 4096 字节块

                        # 打开文件准备写入
                        index = 1
                        with open(save_path, 'wb') as out_file:
                            for buf in dl_file.iter_content(chunk_size=blocksize):
                                if not buf:
                                    break
                                out_file.write(buf)
                                logger.info('{} {} finished {}%'.format(symbol, date_str, index * 10))
                                index += 1

                    logger.info('{} {} save finished'.format(symbol, date_str))

                except Exception as e:
                    logger.error(e)
                    if os.path.exists(save_path):
                        os.remove(save_path)

    @staticmethod
    def get_wsl_ip():
        result = subprocess.run(['wsl', 'hostname', '-I'], stdout=subprocess.PIPE)
        wsl_ip = result.stdout.decode('utf-8').strip().split(' ')[0]
        return wsl_ip

    @classmethod
    def sync_redis(cls, _symbols, _redis_host, _config_port, _node_port):
        exist_keys = []
        symbols = _symbols if isinstance(_symbols, list) else [_symbols]
        loop = asyncio.get_event_loop()
        client = AsyncRedisClient(_redis_host, _config_port)
        node = AsyncRedisClient(_redis_host, _node_port)
        rsp = loop.run_until_complete(client.add_hash(0, 'data_shard', {'{}:{}'.format(_redis_host, _node_port): 1}))
        if not rsp:
            logger.error('add hash failed, check config redis status')
            return
        
        receive_ts_bias = 100000
        folder_path = '../algoData'
        file_list = sorted(os.listdir(folder_path))
        for file_name in file_list:
            zip_file_path = '{}/{}'.format(folder_path, file_name)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                symbol, _ = file_name.split('-', 1)
                if symbol not in symbols:
                    continue

                coro = client.get_hash(0, 'last_ts', '{}|binance_future'.format(symbol))
                last_cache_ts = loop.run_until_complete(coro) or b'0'
                last_cache_ts = int(last_cache_ts.decode())

                _, _, tmp = file_name.split('-', 2)
                date_str, _ = tmp.split('.')
                zip_timestamp = local_date_timestamp(date_str)
                if zip_timestamp <= last_cache_ts:
                    logger.info('{} already cached'.format(file_name))
                    continue

                tmp = symbol.replace('_', '').upper()
                data_name = file_name.replace('zip', 'csv').replace(symbol, tmp)
                insert_list = []
                last_rk_ts = 0
                index = 1

                with zip_ref.open(data_name) as file:
                    logger.info('{} load from disk'.format(file_name))
                    agg_trades = pd.read_csv(file).to_dict('records')
                    logger.info('{} format data'.format(file_name))
                    for trade in agg_trades:
                        timestamp = trade['transact_time'] * 1000
                        direction = 0 if trade['is_buyer_maker'] else 1
                        if timestamp == last_rk_ts:

                            rank_timestamp = last_rk_ts + receive_ts_bias + index
                            index += 1
                        else:
                            rank_timestamp = timestamp + receive_ts_bias
                            index = 1

                        last_rk_ts = timestamp
                        # 生成四个时间序列的key
                        ts_keys = [
                            '{}|binance_future|trade|close'.format(symbol),
                            '{}|binance_future|trade|amount'.format(symbol),
                            '{}|binance_future|trade|timestamp'.format(symbol),
                            '{}|binance_future|trade|direction'.format(symbol)
                        ]
                        # 检查并创建TS
                        for key in ts_keys:
                            if key not in exist_keys:
                                pair, exchange, data_type, field = key.split('|')
                                labels = {'pair': pair, 'exchange': exchange, 'data_type': data_type, 'field': field}
                                rsp = loop.run_until_complete(node.create_ts_key(0, key, labels))
                                exist_keys.append(key)
                        # 添加数据到插入列表

                        insert_list.extend([
                            (ts_keys[0], rank_timestamp, trade['price']),
                            (ts_keys[1], rank_timestamp, trade['quantity']),
                            (ts_keys[2], rank_timestamp, timestamp),
                            (ts_keys[3], rank_timestamp, direction),
                        ])

                    if insert_list:
                        logger.info('{} sync to redis'.format(file_name))
                        coro = node.add_ts_batch(0, insert_list)
                        rsp = loop.run_until_complete(coro)
                        if not rsp:
                            logger.error('add ts batch failed, check node redis status')
                            return

                        coro = client.add_hash(0, 'last_ts', {'{}|binance_future'.format(symbol): zip_timestamp})
                        loop.run_until_complete(coro)

                    logger.info('{} sync finished'.format(file_name))
