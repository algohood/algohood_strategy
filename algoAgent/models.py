from autogen_ext.models.openai import OpenAIChatCompletionClient
from algoConfig.modelConfig import url_dict, api_keys

silicon_meta_llama = OpenAIChatCompletionClient(
    model="meta-llama/Llama-3.3-70B-Instruct",
    base_url=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": 'meta',
    }
)

silicon_deepseek_v3 = OpenAIChatCompletionClient(
    model="Pro/deepseek-ai/DeepSeek-V3",
    base_url=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": 'deepseek',
    }
)

silicon_deepseek_r1 = OpenAIChatCompletionClient(
    model="Pro/deepseek-ai/DeepSeek-R1",
    base_url=url_dict['siliconflow'],
    api_key=api_keys['siliconflow'],
    model_info={
        "vision": False,
        "function_calling": False,
        "json_output": False,
        "family": 'deepseek',
    }
)

deepseek_v3 = OpenAIChatCompletionClient(
    model="deepseek-chat",
    base_url=url_dict['deepseek'],
    api_key=api_keys['deepseek'],
    model_info={
        "vision": False,
        "function_calling": True,
        "json_output": True,
        "family": 'deepseek',
    }
)

deepseek_r1 = OpenAIChatCompletionClient(
    model="deepseek-reasoner",
    base_url=url_dict['deepseek'],
    api_key=api_keys['deepseek'],
    model_info={
        "vision": False,
        "function_calling": False,
        "json_output": False,
        "family": 'deepseek',
    }
)
