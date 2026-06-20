# -*- coding: utf-8 -*-
import os
import sys
import time
import random
import string
import hashlib
import requests
import json

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
            response = requests.get(url, headers=headers, timeout=15) # 增加超时时间
            
            # 如果请求成功，返回 JSON
            if response.status_code == 200:
                return response.json()
            else:
                print(f"请求异常 (状态码: {response.status_code}): {response.text}")
                
        except Exception as e:
            print(f"请求报错 (尝试 {i+1}/{attempts}): {str(e)}")
            time.sleep(3) # 失败后多等几秒
    return None

def main():
    cookie = os.environ.get("MIHOYO_COOKIE")
    if not cookie:
        print("❌ 未找到 MIHOYO_COOKIE")
        sys.exit(1)

    headers = {
        "Cookie": cookie,
        "x-rpc-app_version": "2.68.1", # 【修改点】升级版本号
        "x-rpc-client_type": "5",
        "Referer": "https://webstatic.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("[开始] 正在获取原神玩家数据...")
    
    # 1. 获取首页数据
    index_res = request_with_retry(
        f"https://api-takumi.mihoyo.com/game_record/genshin/api/index?role_id={TARGET_UID}&server={TARGET_SERVER}", 
        headers.copy()
    )
    
    time.sleep(2) # 【修改点】防止高频请求被封
    
    # 2. 获取实时便笺数据
    note_res = request_with_retry(
        f"https://api-takumi.mihoyo.com/game_record/genshin/api/dailyNote?role_id={TARGET_UID}&server={TARGET_SERVER}", 
        headers.copy()
    )

    # 检查返回数据
    if not index_res:
        print("❌ 首页数据获取失败: 接口无响应或网络错误")
        sys.exit(1)
    if index_res.get("retcode") != 0:
        print(f"❌ 首页数据获取失败: {index_res.get('message', '未知错误')}")
        sys.exit(1)
    
    if not note_res:
        print("❌ 便笺数据获取失败: 接口无响应或网络错误")
        sys.exit(1)
    if note_res.get("retcode") != 0:
        print(f"❌ 便笺数据获取失败: {note_res.get('message', '未知错误')}")
        sys.exit(1)

    print("✅ 数据获取成功")
    
    # 提取数据
    stats = index_res["data"]["stats"]
    daily_note = note_res["data"]
    avatars_list = index_res["data"].get("avatars", [])
    
    player_name = index_res["data"].get("nickname", "冒险者")
    player_level = index_res["data"].get("level", 1)
    player_avatar = avatars_list[0].get("image", None) if avatars_list else None
    
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
            } for avatar in avatars_list[:8]
        ],
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ 数据已保存到 data.json")

if __name__ == "__main__":
    main()