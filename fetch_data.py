# -*- coding: utf-8 -*-
"""
模块名称: fetch_data.py
功能描述: 定时调用米游社开放接口，获取特定 UID 的原神战绩与实时便笺数据。
         执行服务端状态码验证与底层数据清洗，输出具备高向下兼容性的结构化 JSON 文件。
安全声明: 严禁在此硬编码任何明文 Cookie。
"""
import os
import sys
import time
import random
import string
import hashlib
import requests
import json

# 全局静态配置：目标账户 UID 与所属官方服务器
TARGET_UID = "257999016"
TARGET_SERVER = "cn_gf01"

def generate_dynamic_secret() -> str:
    """
    生成米游社 API 安全校验所需的 DS (Dynamic Secret) 令牌。
    """
    salt = "xV8v4Qu54xrTH7gZ0aGvFv3YpyCHZBFY"
    current_time = int(time.time())
    random_str = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    
    query_param = f"t={current_time}&r={random_str}"
    sign_source = f"salt={salt}&{query_param}"
    signature = hashlib.md5(sign_source.encode(encoding="utf-8")).hexdigest()
    
    return f"{current_time},{random_str},{signature}"

def execute_data_ingestion():
    """
    执行数据抓取中台的核心业务逻辑。
    """
    cookie_credential = os.environ.get("MIHOYO_COOKIE")
    if not cookie_credential:
        print("[核心错误] 未在系统环境变量中检测到 MIHOYO_COOKIE 凭证，请检查 GitHub Secrets 配置。", file=sys.stderr)
        sys.exit(1)

    # 构造标准移动端安全请求头
    request_headers = {
        "Cookie": cookie_credential,
        "DS": generate_dynamic_secret(),
        "x-rpc-app_version": "2.34.1",
        "x-rpc-client_type": "5",
        "Referer": "https://webstatic.mihoyo.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36"
    }
    
    try:
        index_api_url = f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/index?role_id={TARGET_UID}&server={TARGET_SERVER}"
        note_api_url = f"https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote?role_id={TARGET_UID}&server={TARGET_SERVER}"
        
        print("[进程控制] 正在向米游社网关发起首页数据检索请求...")
        index_response = requests.get(index_api_url, headers=request_headers, timeout=15).json()
        
        print("[进程控制] 正在向米游社网关发起实时便签检索请求...")
        note_response = requests.get(note_api_url, headers=request_headers, timeout=15).json()
        
        # 验证首页接口业务状态码
        if index_response.get("retcode") != 0:
            print(f"[网关拒绝] 首页数据请求失败。错误码: {index_response.get('retcode')}, 提示信息: {index_response.get('message')}", file=sys.stderr)
            print("[故障排查提示] 请确认您的 MIHOYO_COOKIE 是否有效、是否过期，或请求是否被官方风控限制。", file=sys.stderr)
            sys.exit(1)
            
        # 验证实时便签接口业务状态码
        if note_response.get("retcode") != 0:
            print(f"[网关拒绝] 实时便签请求失败。错误码: {note_response.get('retcode')}, 提示信息: {note_response.get('message')}", file=sys.stderr)
            print("[故障排查提示] 请确认您的米游社App中是否已经开启了“实时便签”公开展示开关。", file=sys.stderr)
            sys.exit(1)
            
        # 提取核心数据体
        raw_stats = index_response["data"]["stats"]
        raw_note = note_response["data"]
        
        # 构造高鲁棒性双层数据模型（向下严格匹配 script.js 的嵌套命名空间要求）
        structured_dataset = {
            "stats": raw_stats,
            "daily_note": raw_note
        }
        
        # 执行磁盘 IO 原子化写入
        with open("data.json", "w", encoding="utf-8") as file_handle:
            json.dump(structured_dataset, file_handle, ensure_ascii=False, indent=4)
        print("[执行成功] 数据清洗合并完成，已成功写出到 data.json 静态数据源。")
            
    except Exception as runtime_error:
        print(f"[系统异常] 运行时发生未捕获的严重突发崩溃: {str(runtime_error)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    execute_data_ingestion()