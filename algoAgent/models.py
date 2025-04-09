from langchain_openai import ChatOpenAI
from langchain_deepseek import ChatDeepSeek
from algoConfig.modelConfig import url_dict, api_keys


# doubao_deepseek_r1 = ChatOpenAI(
#     model="deepseek-r1-250120",
#     base_url=url_dict['doubao'],
#     api_key=api_keys['doubao'],
# )

tecent_deepseek_r1 = ChatDeepSeek(
    model_name="deepseek-r1",
    api_base=url_dict['tecent'],
    api_key=api_keys['tecent'],
)

tecent_deepseek_v3 = ChatDeepSeek(
    model_name="deepseek-v3",
    api_base=url_dict['tecent'],
    api_key=api_keys['tecent'],
)

doubao_deepseek_r1 = ChatDeepSeek(
    model_name="deepseek-r1-250120",
    api_base=url_dict['doubao'],
    api_key=api_keys['doubao'],
)

doubao_deepseek_v3 = ChatDeepSeek(
    model_name="deepseek-v3-241226",
    api_base=url_dict['doubao'],
    api_key=api_keys['doubao'],
)

silicon_meta_llama = ChatDeepSeek(
    model_name="meta-llama/Llama-3.3-70B-Instruct",
    api_base=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
)

silicon_deepseek_v3 = ChatDeepSeek(
    model_name="Pro/deepseek-ai/DeepSeek-V3",
    api_base=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
)

silicon_deepseek_r1 = ChatDeepSeek(
    model_name="Pro/deepseek-ai/DeepSeek-R1",
    api_base=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
)

deepseek_v3 = ChatDeepSeek(
    model_name="deepseek-chat",
    api_base=url_dict['deepseek'],
    api_key=api_keys['deepseek'],
)

deepseek_r1 = ChatDeepSeek(
    model_name="deepseek-reasoner",
    api_base=url_dict['deepseek'],
    api_key=api_keys['deepseek'],
)
