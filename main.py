import streamlit as st
import os
import sys
from pathlib import Path

# 确保 func 文件夹可以被导入
sys.path.insert(0, str(Path(__file__).parent / 'func'))

from convert import convert_json_to_csv
from gainscore import score_reviews

st.set_page_config(page_title="Review Analyzer", layout="wide")
st.title("🎮 Steam 评论情感分析工具")

# ---- 侧边栏：API 设置 ----
st.sidebar.header("🔑 DeepSeek API 配置")
api_key = st.sidebar.text_input("API Key", type="password")
base_url = st.sidebar.text_input("Base URL", value="https://api.deepseek.com/v1")
model = st.sidebar.text_input("模型", value="deepseek-reasoner", help="深度思考模型")

# ---- 主界面 Tabs ----
tab1, tab2 = st.tabs(["📥 JSON 转 CSV", "🤖 评论 AI 评分"])

with tab1:
    st.header("转换 JSON 评论文件为 CSV")

    # 列出 o_json 中的所有 JSON 文件
    json_dir = "o_json"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

    selected_json = st.selectbox("选择 JSON 文件", json_files)
    csv_name = st.text_input("输出 CSV 文件名（不含扩展名）", value="output")

    if st.button("开始转换"):
        if selected_json:
            json_path = os.path.join(json_dir, selected_json)
            csv_path = os.path.join("o_csv", f"{csv_name}.csv")
            try:
                convert_json_to_csv(json_path, csv_path)
                st.success(f"✅ 转换完成！文件已保存至 `{csv_path}`")
            except Exception as e:
                st.error(f"转换失败: {e}")
        else:
            st.warning("请先选择一个 JSON 文件")

    st.markdown("---")
    st.info("💡 请将要转换的 JSON 文件放入 `o_json` 文件夹")

with tab2:
    st.header("使用 DeepSeek 为评论打分")

    csv_dir = "o_csv"
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

    selected_csv = st.selectbox("选择 CSV 文件", csv_files)
    output_name = st.text_input("结果文件名（不含扩展名）", value="data")

    if st.button("开始评分", type="primary"):
        if not api_key:
            st.error("请先在侧边栏输入 API Key")
        elif not selected_csv:
            st.error("请选择一个 CSV 文件")
        else:
            csv_path = os.path.join(csv_dir, selected_csv)
            output_path = os.path.join("data", f"{output_name}.csv")

            with st.spinner("🤖 正在调用 DeepSeek 深度思考模型，请稍候..."):
                try:
                    score_reviews(csv_path, output_path, api_key, base_url, model)
                    st.success(f"✅ 评分完成！结果已保存至 `{output_path}`")
                except Exception as e:
                    st.error(f"评分过程出错: {e}")

    st.markdown("---")
    st.info("📌 评分将基于**评论内容**生成情感反馈、长度、情感占比及标签")