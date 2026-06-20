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
    if not cookie:
        print("【错误】未在GitHub后台找到 MIHOYO_COOKIE 密钥！")
        return

    headers = {
        "Cookie": cookie,
        "DS": get_ds(),
        "x-rpc-app_version": "2.34.1",
        "x-rpc-client_type": "5",
        "Referer": "https://webstatic.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36"
    }

    try:
        index_url = f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index?role_id={UID}&server={SERVER}"
        res_index = requests.get(index_url, headers=headers).json()
        
        note_url = f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote?role_id={UID}&server={SERVER}"
        res_note = requests.get(note_url, headers=headers).json()

        if res_index.get("retcode") != 0 or res_note.get("retcode") != 0:
            print("【抓取失败】请检查Cookie或米游社公开开关。")
            return

        idx = res_index["data"]["stats"]
        note = res_note["data"]

        # 计算派遣完成的数量
        expeditions_list = note.get("expeditions", [])
        finished_exp = sum(1 for e in expeditions_list if e.get("status") == "Finished")
        max_exp = note.get("max_expedition_num", 5)

        # ✨ 核心修正：这里和你的 script.js 要求的字段完全合体！
        result = {
            "days": idx.get("active_day_number"),
            "abyss": idx.get("spiral_abyss"),
            "achievements": idx.get("achievement_number"),
            "characters": idx.get("avatar_number"),
            "resin": note.get("current_resin"),
            "max_resin": note.get("max_resin"),
            "coin": note.get("current_home_coin"),
            "task": 4 - note.get("finished_task_num", 0),
            "expeditions": f"{finished_exp}/{max_exp}"  # 格式化输出如 "3/5"
        }

        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print("【成功】data.json 已按前端格式刷新！")

    except Exception as e:
        print(f"运行出错: {e}")

if __name__ == "__main__":
    fetch_data()