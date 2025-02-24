from langchain_openai import ChatOpenAI
from algoConfig.modelConfig import url_dict, api_keys


doubao_deepseek_r1 = ChatOpenAI(
    model="deepseek-r1-250120",
    base_url=url_dict['doubao'],
    api_key=api_keys['doubao'],
)

doubao_deepseek_v3 = ChatOpenAI(
    model="deepseek-v3-241226",
    base_url=url_dict['doubao'],
    api_key=api_keys['doubao'],
)

silicon_meta_llama = ChatOpenAI(
    model="meta-llama/Llama-3.3-70B-Instruct",
    base_url=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
)

silicon_deepseek_v3 = ChatOpenAI(
    model="Pro/deepseek-ai/DeepSeek-V3",
    base_url=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
)

silicon_deepseek_r1 = ChatOpenAI(
    model="Pro/deepseek-ai/DeepSeek-R1",
    base_url=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
)

deepseek_v3 = ChatOpenAI(
    model="deepseek-chat",
    base_url=url_dict['deepseek'],
    api_key=api_keys['deepseek'],
)

deepseek_r1 = ChatOpenAI(
    model="deepseek-reasoner",
    base_url=url_dict['deepseek'],
    api_key=api_keys['deepseek'],
)
