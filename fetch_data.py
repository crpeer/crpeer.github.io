# -*- coding: utf-8 -*-
"""
@file: fetch_data.py
@description: 终极健壮容错版数据抓取脚本。支持指数退避重试，对 5003 等风控错误进行非致命兼容处理，绝不卡死 CI 流程。
"""
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
    """生成米游社常规 Web 端战绩查询专属的 DS 安全校验令牌"""
    salt = "6s25p6x5gqncl09967997hmg9g7g9w0r"
    current_time = int(time.time())
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    
    sign_source = f"salt={salt}&t={current_time}&r={random_str}"
    signature = hashlib.md5(sign_source.encode(encoding="utf-8")).hexdigest()
    
    return f"{current_time},{random_str},{signature}"

def request_with_retry(url, headers, attempts=3, backoff=2):
    """带指数退避的鲁棒网络请求函数"""
    for i in range(attempts):
        try:
            # 每次请求动态更新 DS 令牌防止时效过期
            headers["DS"] = generate_web_ds()
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code == 200:
                return response.json()
            print(f"[WARN] HTTP 状态码异常: {response.status_code}，正在尝试第 {i+1} 次重试...")
        except Exception as e:
            wait_time = backoff ** i
            print(f"[WARN] 请求网络引发突发异常 (尝试 {i+1}/{attempts}): {e}. 将在 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    return None

def execute_data_ingestion():
    cookie_credential = os.environ.get("MIHOYO_COOKIE")
    if not cookie_credential:
        print("[WARN] 未在系统环境中检测到 'MIHOYO_COOKIE' 凭证。跳过本次抓取任务（非致命退出）。")
        sys.exit(0)

    request_headers = {
        "Cookie": cookie_credential,
        "x-rpc-app_version": "2.11.1",
        "x-rpc-client_type": "5",
        "Referer": "https://webstatic.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    index_api_url = f"https://api-takumi.mihoyo.com/game_record/genshin/api/index?role_id={TARGET_UID}&server={TARGET_SERVER}"
    note_api_url = f"https://api-takumi.mihoyo.com/game_record/genshin/api/dailyNote?role_id={TARGET_UID}&server={TARGET_SERVER}"
    
    print("[进程监控] 正在向米游社网关发起首页数据检索请求...")
    index_data = request_with_retry(index_api_url, request_headers)
    
    print("[进程监控] 正在向米游社网关发起实时便签检索请求...")
    note_data = request_with_retry(note_api_url, request_headers)
    
    # 如果所有重试均告失败（如米游社服务器彻底挂了或断网）
    if index_data is None or note_data is None:
        print("[ERROR] 所有的网络请求尝试均已失败。为保护 CI 流程不被破坏，执行非致命性安全退出。")
        sys.exit(0)
        
    # 核心业务错误码熔断容错（重点处理 5003 封控与过期）
    for res_name, res_payload in [("首页战绩", index_data), ("实时便签", note_data)]:
        retcode = res_payload.get("retcode")
        if retcode != 0:
            print(f"\n[网关拒绝] {res_name} 请求失败。错误码: {retcode}, 提示信息: {res_payload.get('message')}")
            print("[故障排查提示] 请确认您的 MIHOYO_COOKIE 是否有效、是否过期，或请求是否被官方风控限制。")
            print("[安全熔断] 检测到已知的外部不可控业务错误，执行非致命性安全退出（Exit 0），保证工作流绿灯。")
            sys.exit(0)

    # 正常流程：成功拿到数据，写入 data.json
    try:
        structured_dataset = {
            "stats": index_data["data"]["stats"],
            "daily_note": note_data["data"]
        }
        with open("data.json", "w", encoding="utf-8") as file_handle:
            json.dump(structured_dataset, file_handle, ensure_ascii=False, indent=4)
        print("[执行成功] 数据管道全线畅通，已成功写出到 data.json。")
    except Exception as parse_error:
        print(f"[ERROR] 解析返回的数据结构时发生突变错误: {parse_error}。安全退出。")
        sys.exit(0)

if __name__ == "__main__":
    execute_data_ingestion()