import openai

def call_deepseek(messages, api_key, base_url="https://api.deepseek.com/v1", model="deepseek-reasoner", temperature=0.1):
    """调用 DeepSeek API，返回助手回复内容"""
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content