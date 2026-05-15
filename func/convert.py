import json
import pandas as pd
import os
import re
from bs4 import BeautifulSoup

def build_rows_from_reviews(reviews):
    """从原始 reviews 列表构建行数据（适用于 CSgo.json 格式）"""
    rows = []
    for rev in reviews:
        row = {
            'recommendationid': rev.get('recommendationid'),
            'language': rev.get('language'),
            'review': rev.get('review'),
            'timestamp_created': rev.get('timestamp_created'),
            'timestamp_updated': rev.get('timestamp_updated'),
            'voted_up': rev.get('voted_up'),
            'votes_up': rev.get('votes_up'),
            'votes_funny': rev.get('votes_funny'),
            'weighted_vote_score': rev.get('weighted_vote_score'),
            'comment_count': rev.get('comment_count'),
            'steam_purchase': rev.get('steam_purchase'),
            'received_for_free': rev.get('received_for_free'),
            'refunded': rev.get('refunded'),
            'written_during_early_access': rev.get('written_during_early_access'),
            'primarily_steam_deck': rev.get('primarily_steam_deck'),
            'app_release_date': rev.get('app_release_date'),
        }

        author = rev.get('author', {})
        for k, v in author.items():
            row[f'author_{k}'] = v

        hardware = rev.get('hardware', {})
        if hardware:
            for k, v in hardware.items():
                row[f'hardware_{k}'] = v

        reactions = rev.get('reactions', [])
        row['reactions_total'] = sum(r.get('count', 0) for r in reactions)

        rows.append(row)
    return rows

def parse_html_reviews(html_str):
    """从 steamBS1.json 的 html 字段中解析评测列表"""
    soup = BeautifulSoup(html_str, 'html.parser')
    review_boxes = soup.find_all('div', class_='review_box')
    rows = []

    for idx, box in enumerate(review_boxes):
        row = {
            # 基础字段
            'recommendationid': f'html_{idx}',            # 无原ID，生成一个唯一值
            'language': 'schinese',                       # 页面为中文
            'review': '',
            'timestamp_created': None,
            'timestamp_updated': None,
            'voted_up': False,
            'votes_up': 0,
            'votes_funny': 0,
            'weighted_vote_score': None,
            'comment_count': 0,
            'steam_purchase': True,                       # 默认为 Steam 购买
            'received_for_free': False,
            'refunded': False,
            'written_during_early_access': False,
            'primarily_steam_deck': False,
            'app_release_date': None,
            # 作者字段
            'author_steamid': None,
            'author_personaname': None,
            'author_persona_status': None,
            'author_profile_url': None,
            'author_num_games_owned': None,
            'author_num_reviews': None,
            'author_playtime_forever': None,
            'author_playtime_last_two_weeks': None,
            'author_playtime_at_review': None,
            'author_last_played': None,
            'author_avatar': None,
            # 硬件字段（可能部分存在）
            'hardware_manufacturer': None,
            'hardware_model': None,
            'hardware_dx_video_card': None,
            'hardware_dx_vendorid': None,
            'hardware_dx_deviceid': None,
            'hardware_num_gpu': None,
            'hardware_system_ram': None,
            'hardware_os': None,
            'hardware_cpu_vendor': None,
            'hardware_cpu_name': None,
            'hardware_gaming_device_type': None,
            'hardware_dx_driver_version': None,
            'hardware_adapter_description': None,
            'hardware_driver_version': None,
            'hardware_driver_date': None,
            'hardware_vram_size': None,
            'hardware_screen_width': None,
            'hardware_screen_height': None,
            'reactions_total': 0
        }

        # ---------- 评论内容 ----------
        content_div = box.find('div', class_='content')
        if content_div:
            row['review'] = content_div.get_text(separator='\n', strip=True)

        # ---------- 发布日期 & 时间戳 ----------
        posted_div = box.find('div', class_='postedDate')
        if posted_div:
            date_text = posted_div.get_text(strip=True)
            row['timestamp_created'] = date_text
            row['timestamp_updated'] = date_text

        # ---------- 是否推荐 ----------
        title_div = box.find('div', class_='title')
        if title_div:
            row['voted_up'] = '推荐' in title_div.get_text()

        # ---------- 好评数 / 有趣数 ----------
        vote_info = box.find('div', class_='vote_info')
        if vote_info:
            text = vote_info.get_text()
            match = re.search(r'有\s*(\d+)\s*人觉得这篇评测有价值', text)
            if match:
                row['votes_up'] = int(match.group(1))
            match_funny = re.search(r'有\s*(\d+)\s*人觉得这篇评测很欢乐', text)
            if match_funny:
                row['votes_funny'] = int(match_funny.group(1))

        # ---------- Steam Deck 标识 ----------
        if box.find('img', class_='majority_deck'):
            row['primarily_steam_deck'] = True

        # ---------- 作者信息 ----------
        # 用户名 & 个人资料链接
        persona_div = box.find('div', class_='persona_name')
        if persona_div:
            a_tag = persona_div.find('a')
            if a_tag:
                row['author_personaname'] = a_tag.get_text(strip=True)
                row['author_profile_url'] = a_tag.get('href')
                # 从 profile URL 提取 steamid
                match = re.search(r'/profiles/(\d+)/', row['author_profile_url'])
                if match:
                    row['author_steamid'] = match.group(1)

        # 在线状态
        avatar_div = box.find('div', class_='playerAvatar')
        if avatar_div:
            classes = avatar_div.get('class', [])
            if 'online' in classes:
                row['author_persona_status'] = 'online'
            elif 'offline' in classes:
                row['author_persona_status'] = 'offline'
            elif 'in-game' in classes:
                row['author_persona_status'] = 'in-game'
            else:
                row['author_persona_status'] = 'unknown'
            # 头像 URL
            img = avatar_div.find('img')
            if img:
                row['author_avatar'] = img.get('src')

        # 拥有游戏数 & 评测数
        counts_div = box.find('div', class_='author_counts')
        if counts_div:
            owned = counts_div.find('div', class_='num_owned_games')
            if owned:
                match = re.search(r'(\d+)\s*款游戏', owned.get_text())
                if match:
                    row['author_num_games_owned'] = int(match.group(1))
            revs = counts_div.find('div', class_='num_reviews')
            if revs:
                match = re.search(r'(\d+)\s*篇评测', revs.get_text())
                if match:
                    row['author_num_reviews'] = int(match.group(1))

        # 游戏时间
        hours_div = box.find('div', class_='hours ellipsis')
        if hours_div:
            text = hours_div.get_text(strip=True)
            # 总时数
            match_total = re.search(r'总时数\s*([\d.]+)\s*小时', text)
            if match_total:
                row['author_playtime_forever'] = float(match_total.group(1))
            # 评测时游戏时间
            match_review = re.search(r'评测时\s*([\d.]+)\s*小时', text)
            if match_review:
                row['author_playtime_at_review'] = float(match_review.group(1))
            else:
                row['author_playtime_at_review'] = row['author_playtime_forever']

        # ---------- 硬件信息 ----------
        hw_container = box.find('div', class_='reviewer_hardware_container')
        if hw_container:
            items = hw_container.find_all('div', class_='reviewer_hardware_item')
            for item in items:
                text = item.get_text(strip=True)
                if 'Windows' in text or 'macOS' in text or 'Linux' in text:
                    row['hardware_os'] = text
                elif 'RAM' in text:
                    match = re.search(r'RAM：(\d+)\s*GB', text)
                    if match:
                        row['hardware_system_ram'] = int(match.group(1)) * 1024   # 转为 MB
                elif 'VRAM' in text:
                    match = re.search(r'VRAM：(\d+)\s*GB', text)
                    if match:
                        row['hardware_vram_size'] = int(match.group(1)) * 1024
                elif 'CPU' in text:
                    row['hardware_cpu_name'] = text
                elif 'GPU' in text or 'NVIDIA' in text or 'AMD' in text:
                    row['hardware_dx_video_card'] = text

        rows.append(row)

    return rows

def convert_json_to_csv(json_path, csv_path):
    """读取 JSON 并转换为 CSV，自动识别两种格式"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 判断格式
    if 'reviews' in data and isinstance(data['reviews'], list):
        # CSgo.json 格式
        rows = build_rows_from_reviews(data['reviews'])
    elif 'html' in data:
        # steamBS1.json 格式
        rows = parse_html_reviews(data['html'])
    else:
        raise ValueError("无法识别的 JSON 格式：既没有 'reviews' 也没有 'html' 字段")

    df = pd.DataFrame(rows)

    # 列名中文化映射
    rename_dict = {
        'recommendationid': '推荐ID',
        'language': '语言',
        'review': '评论内容',
        'timestamp_created': '创建时间戳',
        'timestamp_updated': '更新时间戳',
        'voted_up': '是否好评',
        'votes_up': '好评数',
        'votes_funny': '有趣票数',
        'weighted_vote_score': '加权评分',
        'comment_count': '评论数',
        'steam_purchase': 'Steam购买',
        'received_for_free': '免费获得',
        'refunded': '已退款',
        'written_during_early_access': '抢先体验期间撰写',
        'primarily_steam_deck': '主要使用SteamDeck',
        'app_release_date': '应用发布日期',
        'author_steamid': 'Steam ID',
        'author_personaname': '用户名',
        'author_persona_status': '在线状态',
        'author_profile_url': '个人资料链接',
        'author_num_games_owned': '拥有游戏数',
        'author_num_reviews': '用户评论数',
        'author_playtime_forever': '总游戏时间',
        'author_playtime_last_two_weeks': '近两周游戏时间',
        'author_playtime_at_review': '评论时游戏时间',
        'author_last_played': '最后游玩时间戳',
        'author_avatar': '头像',
        'hardware_manufacturer': '主板制造商',
        'hardware_model': '主板型号',
        'hardware_dx_video_card': '显卡',
        'hardware_dx_vendorid': '显卡厂商ID',
        'hardware_dx_deviceid': '显卡设备ID',
        'hardware_num_gpu': 'GPU数量',
        'hardware_system_ram': '系统内存(MB)',
        'hardware_os': '操作系统',
        'hardware_cpu_vendor': 'CPU厂商',
        'hardware_cpu_name': 'CPU名称',
        'hardware_gaming_device_type': '游戏设备类型',
        'hardware_dx_driver_version': 'DirectX驱动版本',
        'hardware_adapter_description': '显卡描述',
        'hardware_driver_version': '驱动版本',
        'hardware_driver_date': '驱动日期',
        'hardware_vram_size': '显存(MB)',
        'hardware_screen_width': '屏幕宽度',
        'hardware_screen_height': '屏幕高度',
        'reactions_total': '反应总数'
    }

    # 只保留映射中存在的列，避免缺失列导致错误
    existing_columns = [col for col in rename_dict.keys() if col in df.columns]
    df = df[existing_columns]
    df.rename(columns=rename_dict, inplace=True)

    os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f'转换完成，共 {len(df)} 条记录，保存至 {csv_path}')

# 使用示例（可直接运行）
if __name__ == '__main__':
    # 测试 CSgo.json
    # convert_json_to_csv('CSgo.json', 'output_CSgo.csv')
    # 测试 steamBS1.json
    # convert_json_to_csv('steamBS1.json', 'output_steamBS1.csv')
    pass