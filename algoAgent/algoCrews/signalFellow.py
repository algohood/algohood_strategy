import asyncio
import importlib.util
import os
from algoUtils.agentUtil import StreamingSocietyOfMindAgent
from algoUtils.agentUtil import AssistantAgent
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from algoAgent.models import *
from algoUtils.autoGenUtil import custom_output


def save_code(name: str, code: str):
    """
    name: 文件名
    code: 代码
    """
    # 检查文件是否存在
    spec = importlib.util.find_spec('algoStrategy')
    package_path = spec.submodule_search_locations[0]
    file_path = os.path.join(package_path, 'algoSignals/{}.py'.format(name))
    if os.path.exists(file_path):
        print(f"文件{file_path}已存在，跳过保存")
        return
    
    # 保存代码
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"文件{file_path}保存成功")


class AiSignal:
    planner_agent = AssistantAgent(
        name="planner_agent",
        model_client=silicon_deepseek_v3,
        system_message="""
            你是一个高频量化交易员，对整个量化策略开发流程非常熟悉，尤其是信号开发阶段。
            具体任务是，你将使用事件驱动型增量逐笔成交数据，根据用户需求，为用户推荐相应信号逻辑，并给出信号逻辑的详细说明。
            在给出的信号逻辑中，不讨论后续交易策略等环节内容，只讨论信号逻辑
            要非常清楚所用数据得以下特征
            - 实时推送的**事件驱动型增量数据**（默认是逐笔成交）
            - 数据按实际发生时间推送**无固定频率**
            - 同一时间窗口的数据**可能分多次到达**
            - 数据中包含如下字段
                - recv_ts（数据接收时间戳，单位秒，保留6位小数）
                - delay（数据延迟时间，单位秒，保留6位小数）
                - price（价格）
                - amount（数量）
                - direction（方向 1买/-1卖）
            只需对逻辑进行讨论，不需要给出任何实现相关得解释说明
            默认回复风格简洁明了，除非用户要求进行详细说明后，再进行详细说明
            每次都询问用户是否满足要求，若不满足，则继续讨论；若用户满足，则回复“那接下来由logic_manager对需求进行总结陈述”
        """,
        model_client_stream=True,
    )

    planner_proxy_agent = UserProxyAgent(
        name="planner_proxy_agent",
        description="""
            请与planner_agent沟通和交流你的想法，直到您满意得情况下，回复"我很满意"
        """,
    )

    coding_proxy_agent = UserProxyAgent(
        name="coding_proxy_agent",
        description="""
            请与coding_agent沟通和交流你的想法，直到您满意得情况下，回复"我很满意"
        """,
    )

    end_proxy_agent = UserProxyAgent(
        name="end_proxy_agent",
        description="""
            请与end_agent沟通和交流你的想法，直到您满意得情况下，回复"结束"
        """,
    )

    coding_agent = AssistantAgent(
        name="coding_agent",
        model_client=silicon_deepseek_v3,
        model_client_stream=True,
        system_message="""
            你是一个专业的量化工程师，你非常善于将用户交易信号思路，转化为符合既有交易框架范式的代码
            以下是交易框架中要求实现得规则：
            - 必须首先导入基类：from algoUtils.baseUtil import SignalBase
            - 必须导入输出数据结构：from algoUtils.schemaUtil import Signal
            - 必须创建（若不存在）继承自SignalBase的Algo类，覆写函数generate_signals；函数将被多次调用（每次有新数据到达时）
            - 函数签名为generate_signals(self, _data: Dict[str, List[List]]) -> Optional[List[Signal]]，严格按照签名执行
            - _data是市场实时推送的**事件驱动型增量数据**（默认是逐笔成交）；主要特点是，数据按实际发生时间推送**无固定频率**，同一时间窗口的数据**可能分多次到达**，数据结构示例：
                {
                    "btc_usdt|binance_future": [
                        [recv_ts（单位秒，保留6位小数）, delay（单位秒，保留6位小数）, price（价格）, amount（数量）, direction（方向 1买/-1卖）],
                        ...更多tick数据
                    ],
                    ...其他symbol
                }
            - 根据函数签名得返回值，严格按照返回值结构执行，其中Signal是pydantic数据类，数据结构如下：
                class Signal(BaseModel):
                    batch_id: str  # str(uuid)
                    symbol: str  # 'btc_usdt|binance_future'
                    action: str  # 'open' or 'close'
                    position: str  # 'long' or 'short'

            - 逻辑所需参数，平铺在__init__（）中，且不与已有参数共用， 示例如下:
                def __init__(self, _backward_window):
                    self.backward_window = _backward_window
            - 所有函数的参数命名加前导下划线，正确示例：_price_grid，错误示例：price_grid（缺少前导下划线）、_priceGrid（使用驼峰而非蛇形）
            - 不需要考虑工程上的优化，只需要考虑逻辑中运算性能即可；避免使用性能不好的库，例如pd；尽量使用np进行向量化操作，避免循环操作
            - 补齐所有代码中用到的库
            - 仅返回代码和逻辑说明
            - 每次都询问用户是否满足要求，若不满足，则继续讨论；若用户满足，则回复“那接下来由coding_manager给出最终代码脚本”
        """,
    )

    logic_team = RoundRobinGroupChat(
        participants=[planner_proxy_agent, planner_agent],
        termination_condition=TextMentionTermination("总结陈述"),
    )

    logic_manager = StreamingSocietyOfMindAgent(
        name="logic_manager",
        team=logic_team,
        model_client=silicon_deepseek_v3,
        model_client_stream=True,
        instruction="""
            你是一个专业的量化工程师，你非常善于将用户的交易信号思路，转化为可配置参数和实现逻辑两部分
            后续的讨论是planner_proxy_agent与planner_agent关于交易信号的讨论，你需要选出planner_proxy_agent喜欢得方案
            明确方案后，将从以下两个方面进行总结：
            - 可配置参数：要给出**变量名，变量说明，变量类型，变量默认值**
            - 信号说明：对信号逻辑进行详细说明，包括信号的计算方法、计算逻辑、计算公式等**不需要伪代码**
            最后加一句回复“接下来由coding_agent进行代码实现，用户可与其沟通讨论！”
        """
    )

    coding_team = RoundRobinGroupChat(
        participants=[coding_agent, coding_proxy_agent],
        termination_condition=TextMentionTermination("最终代码脚本"),
    )

    coding_manager = StreamingSocietyOfMindAgent(
        name="coding_manager",
        team=coding_team,
        model_client=silicon_deepseek_v3,
        model_client_stream=True,
        instruction="""
            你是一个专业的量化工程师组长，非常善于将组内讨论得到的代码进行梳理，并生成最终代码脚本
            以下是组内讨论得到的代码，你需要：
            - 将整个业务逻辑流程写入函数注释
            - 添加明确参数注释
            - 注释同一使用中文
            最终只返回代码脚本
            最后加一句回复“接下来由saving_agent进行代码保存”
        """
    )

    saving_agent = AssistantAgent(
        name="saving_agent",
        model_client=silicon_deepseek_v3,
        tools=[save_code],
        system_message="""
            你是一个专业的量化工程师团队负责人
            将讨论后的最终代码，通过save_code工具保存到本地，且不需要做其他任何操作
            起一个好玩且简短得文件名
            文件命名使用lowerCamelCase，示例：activeMarketSignal
        """
    )

    flow = RoundRobinGroupChat(
        participants=[logic_manager, coding_manager, saving_agent],
        max_turns=3,
    )

    @classmethod
    def run(cls):
        asyncio.run(custom_output(cls.flow, ignore_agents=["proxy_agent", "saving_agent"]))


if __name__ == "__main__":
    AiSignal.run()
