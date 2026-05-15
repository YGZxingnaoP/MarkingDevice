import pandas as pd
from deepseek import call_deepseek

def score_reviews(csv_path, output_csv_path, api_key, base_url, model):
    """读取 CSV，提取评论，一次性发给 DeepSeek 评分，然后保存结果"""
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    reviews = df['评论内容'].tolist()

    # 构造 prompt：所有评论一次性发送，要求严格格式化输出
    prompt = "请对以下每条 Steam 用户评论进行评分，严格按照指定格式返回，每条评分之间用 \"---\" 分隔。\n"
    prompt += "评分项目：情感反馈（1-10，1极其负面，10极其正面）、回复长度（1短，2中，3长）、情感占比（1纯理性，10纯情感）、标签（关键词，逗号分隔）。\n"
    prompt += "回复格式示例：情感反馈：5 | 回复长度：1 | 情感占比：7 | 标签：激动，抱怨\n"
    prompt += "请确保每条评论都按此格式返回，不要额外解释。\n\n"

    for idx, text in enumerate(reviews, start=1):
        prompt += f"{idx}. {text}\n"

    prompt += "\n请开始评分："

    messages = [{"role": "user", "content": prompt}]

    ai_response = call_deepseek(messages, api_key, base_url, model, temperature=0.1)

    # 将原始数据与评分整合并保存
    from save import save_results
    save_results(csv_path, output_csv_path, ai_response)
    return ai_response