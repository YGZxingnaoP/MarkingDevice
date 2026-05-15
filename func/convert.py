import json
import pandas as pd
import os

def convert_json_to_csv(json_path, csv_path):
    """读取 JSON 并转换为 CSV，列名已中文化"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    reviews = data.get('reviews', [])
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

    df = pd.DataFrame(rows)

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

    df.rename(columns=rename_dict, inplace=True)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f'转换完成，共 {len(df)} 条记录，保存至 {csv_path}')