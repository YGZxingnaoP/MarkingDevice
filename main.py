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

    # 确保目录存在
    json_dir = "o_json"
    csv_dir = "o_csv"
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

    if not json_files:
        st.warning("⚠️ `o_json` 文件夹中没有找到 JSON 文件，请先放入文件。")
    else:
        # ----- 单文件转换 -----
        st.subheader("📄 单文件转换")
        selected_json = st.selectbox("选择 JSON 文件", json_files, key="single_json")
        # 默认输出名 = 选中的 JSON 文件名（去掉扩展名）
        default_csv_name = os.path.splitext(selected_json)[0] if selected_json else "output"
        csv_name = st.text_input("输出 CSV 文件名（不含扩展名）", value=default_csv_name, key="single_csv_name")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("开始转换", key="single_convert"):
                if selected_json:
                    json_path = os.path.join(json_dir, selected_json)
                    csv_path = os.path.join(csv_dir, f"{csv_name}.csv")
                    try:
                        convert_json_to_csv(json_path, csv_path)
                        st.success(f"✅ 转换完成！文件已保存至 `{csv_path}`")
                    except Exception as e:
                        st.error(f"转换失败: {e}")
                else:
                    st.warning("请先选择一个 JSON 文件")

        # ----- 批量转换 -----
        st.subheader("📦 批量转换")
        st.markdown(f"将转换 **{len(json_files)}** 个 JSON 文件，输出文件名与 JSON 文件名相同（扩展名改为 .csv）")

        with col2:
            if st.button("🚀 一键批量转换所有 JSON", key="batch_convert"):
                success_count = 0
                fail_list = []
                progress_bar = st.progress(0, text="准备转换...")
                status_text = st.empty()

                for i, filename in enumerate(json_files):
                    status_text.text(f"正在转换: {filename} ({i+1}/{len(json_files)})")
                    json_path = os.path.join(json_dir, filename)
                    base_name = os.path.splitext(filename)[0]
                    csv_path = os.path.join(csv_dir, f"{base_name}.csv")
                    try:
                        convert_json_to_csv(json_path, csv_path)
                        success_count += 1
                    except Exception as e:
                        fail_list.append(f"{filename} -> {str(e)}")
                    progress_bar.progress((i + 1) / len(json_files), text=f"进度: {i+1}/{len(json_files)}")

                status_text.empty()
                progress_bar.empty()

                if fail_list:
                    st.error(f"批量转换完成，成功 {success_count} 个，失败 {len(fail_list)} 个：\n" + "\n".join(fail_list))
                else:
                    st.success(f"🎉 批量转换完成！共 {success_count} 个文件已保存至 `{csv_dir}` 文件夹")

    st.markdown("---")
    st.info("💡 请将要转换的 JSON 文件放入 `o_json` 文件夹，转换后的 CSV 文件将保存在 `o_csv` 文件夹中。")

# ======================== Tab2: AI 评分 ========================
with tab2:
    st.header("使用 DeepSeek 为评论打分")

    csv_dir = "o_csv"
    result_dir = "data"
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(result_dir, exist_ok=True)

    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

    if not csv_files:
        st.warning("⚠️ `o_csv` 文件夹中没有找到 CSV 文件，请先转换 JSON 文件。")
    else:
        # ----- 单文件评分 -----
        st.subheader("📄 单文件评分")
        selected_csv = st.selectbox("选择 CSV 文件", csv_files, key="single_csv")
        default_output_name = os.path.splitext(selected_csv)[0] if selected_csv else "data"
        output_name = st.text_input("结果文件名（不含扩展名）", value=default_output_name, key="single_output_name")

        if st.button("开始评分", type="primary", key="single_score"):
            if not api_key:
                st.error("请先在侧边栏输入 API Key")
            elif not selected_csv:
                st.error("请选择一个 CSV 文件")
            else:
                csv_path = os.path.join(csv_dir, selected_csv)
                output_path = os.path.join(result_dir, f"{output_name}.csv")

                with st.spinner("🤖 正在调用 DeepSeek 深度思考模型，请稍候..."):
                    try:
                        score_reviews(csv_path, output_path, api_key, base_url, model)
                        st.success(f"✅ 评分完成！结果已保存至 `{output_path}`")
                    except Exception as e:
                        st.error(f"评分过程出错: {e}")

        # ----- 批量评分（带10秒间隔）-----
        st.subheader("📦 批量评分")
        st.markdown(f"将对 **{len(csv_files)}** 个 CSV 文件逐一进行 AI 评分，**每个文件评分后等待 10 秒**，避免 API 限流。")
        st.markdown("输出文件将自动保存在 `data/` 文件夹中，文件名格式为 `原CSV文件名_scored.csv`。")

        if st.button("🚀 一键批量评分所有 CSV", type="primary", key="batch_score"):
            if not api_key:
                st.error("请先在侧边栏输入 API Key")
            else:
                success_count = 0
                fail_list = []
                progress_bar = st.progress(0, text="准备评分...")
                status_text = st.empty()

                for i, filename in enumerate(csv_files):
                    status_text.text(f"正在评分: {filename} ({i+1}/{len(csv_files)})")
                    csv_path = os.path.join(csv_dir, filename)
                    base_name = os.path.splitext(filename)[0]
                    output_path = os.path.join(result_dir, f"{base_name}_scored.csv")

                    try:
                        score_reviews(csv_path, output_path, api_key, base_url, model)
                        success_count += 1
                        # 如果不是最后一个文件，则等待10秒
                        if i < len(csv_files) - 1:
                            status_text.text(f"等待 10 秒后继续... (已完成 {i+1}/{len(csv_files)})")
                            time.sleep(10)
                    except Exception as e:
                        fail_list.append(f"{filename} -> {str(e)}")

                    progress_bar.progress((i + 1) / len(csv_files), text=f"进度: {i+1}/{len(csv_files)}")

                status_text.empty()
                progress_bar.empty()

                if fail_list:
                    st.error(f"批量评分完成，成功 {success_count} 个，失败 {len(fail_list)} 个：\n" + "\n".join(fail_list))
                else:
                    st.success(f"🎉 批量评分完成！共 {success_count} 个文件已保存至 `{result_dir}` 文件夹")

    st.markdown("---")
    st.info("📌 评分将基于**评论内容**生成情感反馈、长度、情感占比及标签")