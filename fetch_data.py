import os
import time
import random
import string
import hashlib
import requests
import json

# 绑定你的UID和服务器
UID = "257999016"
SERVER = "cn_gf01"

def get_ds():
    salt = "xV8v4Qu54xrTH7gZ0aGvFv3YpyCHZBFY"
    t = int(time.time())
    r = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    main = f"t={t}&r={r}"
    ds = hashlib.md5(f"salt={salt}&{main}".encode()).hexdigest()
    return f"{t},{r},{ds}"

def fetch_data():
    cookie = os.environ.get("MIHOYO_COOKIE")
    headers = {"Cookie": cookie, "DS": get_ds(), "x-rpc-app_version": "2.34.1", "x-rpc-client_type": "5", "Referer": "https://webstatic.mihoyo.com/", "User-Agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36"}
    
    # 获取数据
    index_res = requests.get(f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index?role_id={UID}&server={SERVER}", headers=headers).json()
    note_res = requests.get(f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote?role_id={UID}&server={SERVER}", headers=headers).json()

    if index_res["retcode"] == 0 and note_res["retcode"] == 0:
        idx = index_res["data"]["stats"]
        note = note_res["data"]
        
        # 定义扁平化的数据结构（直接存储最需要的值）
        result = {
            "days": idx.get("active_day_number"),
            "abyss": idx.get("spiral_abyss"),
            "achievements": idx.get("achievement_number"),
            "characters": idx.get("avatar_number"),
            "resin": note.get("current_resin"),
            "max_resin": note.get("max_resin"),
            "coin": note.get("current_home_coin"),
            "task": 4 - note.get("finished_task_num", 0),
            "expeditions": f"{sum(1 for e in note.get('expeditions', []) if e.get('status') == 'Finished')}/{note.get('max_expedition_num', 5)}"
        }
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_data()