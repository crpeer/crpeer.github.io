# -*- coding: utf-8 -*-
import os
import sys
import time
import random
import string
import hashlib
import requests
import json

# 请确保你的 GitHub Secrets 中已经设置了 MIHOYO_COOKIE
# UID 和 Server 固定，直接写在代码里
TARGET_UID = "257999016"
TARGET_SERVER = "cn_gf01"

def generate_web_ds() -> str:
    salt = "6s25p6x5gqncl09967997hmg9g7g9w0r"
    current_time = int(time.time())
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    sign_source = f"salt={salt}&t={current_time}&r={random_str}"
    signature = hashlib.md5(sign_source.encode(encoding="utf-8")).hexdigest()
    return f"{current_time},{random_str},{signature}"

def request_with_retry(url, headers, attempts=3):
    for i in range(attempts):
        try:
            headers["DS"] = generate_web_ds()
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"请求失败 (尝试 {i+1}/{attempts}):", str(e))
            time.sleep(2)
    return None

def main():
    cookie = os.environ.get("MIHOYO_COOKIE")
    if not cookie:
        print("❌ 未找到 MIHOYO_COOKIE")
        sys.exit(0)

    headers = {
        "Cookie": cookie,
        "x-rpc-app_version": "2.11.1",
        "x-rpc-client_type": "5",
        "Referer": "https://webstatic.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("[开始] 正在获取原神玩家数据...")
    
    # 获取首页数据（包含统计信息和角色列表）
    index_res = request_with_retry(
        f"https://api-takumi.mihoyo.com/game_record/genshin/api/index?role_id={TARGET_UID}&server={TARGET_SERVER}", 
        headers.copy()
    )
    
    # 获取实时便笺数据
    note_res = request_with_retry(
        f"https://api-takumi.mihoyo.com/game_record/genshin/api/dailyNote?role_id={TARGET_UID}&server={TARGET_SERVER}", 
        headers.copy()
    )

    # 检查数据是否有效
    if not index_res or index_res.get("retcode") != 0:
        print(f"❌ 首页数据获取失败: {index_res.get('message', '未知错误') if index_res else '无响应'}")
        sys.exit(0)
    
    if not note_res or note_res.get("retcode") != 0:
        print(f"❌ 便笺数据获取失败: {note_res.get('message', '未知错误') if note_res else '无响应'}")
        sys.exit(0)

    print("✅ 数据获取成功")
    
    # 提取统计数据
    stats = index_res["data"]["stats"]
    daily_note = note_res["data"]
    
    # 提取角色数据（获取头像 URL）
    avatars_list = index_res["data"].get("avatars", [])
    
    # 获取首个角色的头像（通常是当前展示的角色）
    player_avatar = None
    player_name = index_res["data"].get("nickname", "冒险者")
    player_level = index_res["data"].get("level", 1)
    
    if avatars_list and len(avatars_list) > 0:
        # 获取第一个角色作为展示头像
        first_avatar = avatars_list[0]
        player_avatar = first_avatar.get("image", None)
        player_name = first_avatar.get("name", player_name)
        print(f"✅ 获取到角色头像: {player_name}")
    
    # 构建最终数据
    data = {
        "stats": stats,
        "daily_note": daily_note,
        "player": {
            "name": player_name,
            "level": player_level,
            "uid": TARGET_UID,
            "avatar": player_avatar,
            "server": "天空岛" if TARGET_SERVER == "cn_gf01" else "世界树"
        },
        "avatars": [
            {
                "name": avatar.get("name", "未知"),
                "level": avatar.get("level", 1),
                "rarity": avatar.get("rarity", 4),
                "image": avatar.get("image", None)
            } for avatar in avatars_list[:8]  # 只保留前 8 个角色
        ],
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # 写入 data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 数据已保存到 data.json (更新时间: {data['last_updated']})")
    sys.exit(0)

if __name__ == "__main__":
    main()
