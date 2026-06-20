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
        except Exception:
            time.sleep(2)
    return None

def main():
    cookie = os.environ.get("MIHOYO_COOKIE")
    if not cookie:
        sys.exit(0)

    headers = {
        "Cookie": cookie,
        "x-rpc-app_version": "2.11.1",
        "x-rpc-client_type": "5",
        "Referer": "https://webstatic.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    index_res = request_with_retry(f"https://api-takumi.mihoyo.com/game_record/genshin/api/index?role_id={TARGET_UID}&server={TARGET_SERVER}", headers)
    note_res = request_with_retry(f"https://api-takumi.mihoyo.com/game_record/genshin/api/dailyNote?role_id={TARGET_UID}&server={TARGET_SERVER}", headers)

    if index_res and note_res and index_res.get("retcode") == 0 and note_res.get("retcode") == 0:
        data = {
            "stats": index_res["data"]["stats"],
            "daily_note": note_res["data"]
        }
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    sys.exit(0)

if __name__ == "__main__":
    main()