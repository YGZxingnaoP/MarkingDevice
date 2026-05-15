import pandas as pd
import re
import os

def save_results(original_csv_path, output_csv_path, ai_result,
                 content_col='评论内容',
                 score_cols=None):

    if score_cols is None:
        score_cols = ['是否好评', '好评数', '有趣票数', '加权评分']

    df = pd.read_csv(original_csv_path, encoding='utf-8-sig')

    # 检查必需的列是否存在
    if content_col not in df.columns:
        raise KeyError(f"原始 CSV 中缺少评论内容列 '{content_col}'")
    missing_score_cols = [col for col in score_cols if col not in df.columns]
    if missing_score_cols:
        raise KeyError(f"原始 CSV 中缺少以下评分列: {missing_score_cols}")

    # 按分隔符切分出每条评论的评分
    parts = [p.strip() for p in ai_result.split('---') if p.strip()]

    if len(parts) != len(df):
        raise ValueError(f"AI 返回的评分条目数({len(parts)})与评论数({len(df)})不匹配，请检查。")

    scores_list = []
    for part in parts:
        emotion_match = re.search(r'情感反馈[：:]\s*(\d+)', part)
        length_match = re.search(r'回复长度[：:]\s*(\d+)', part)
        ratio_match = re.search(r'情感占比[：:]\s*(\d+)', part)
        tag_match = re.search(r'标签[：:]\s*(.+)', part)

        emotion = int(emotion_match.group(1)) if emotion_match else None
        length = int(length_match.group(1)) if length_match else None
        ratio = int(ratio_match.group(1)) if ratio_match else None
        tags = tag_match.group(1).strip() if tag_match else ''

        scores_list.append({
            '情感反馈': emotion,
            '回复长度': length,
            '情感占比': ratio,
            '标签': tags
        })

    scores_df = pd.DataFrame(scores_list)

    # 只保留评论内容、指定的原始评分列、AI 新生成的四个字段
    cols_to_keep = [content_col] + score_cols
    result_df = pd.concat([
        df[cols_to_keep].reset_index(drop=True),
        scores_df
    ], axis=1)

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f'结果已保存至 {output_csv_path}')