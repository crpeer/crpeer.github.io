# -*- coding: utf-8 -*-
"""
模块名称: fetch_data.py
功能描述: 定时调用米游社开放接口，获取特定 UID 的原神战绩与实时便笺数据。
         执行服务端状态码验证与底层数据清洗，输出具备高向上兼容性的结构化 JSON 文件。
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

# 全局静态配置：目标账户 UID 与所属服务器
TARGET_UID = "257999016"
TARGET_SERVER = "cn_gf01"

def generate_dynamic_secret() -> str:
    """
    生成米游社 API 安全校验所需的 DS (Dynamic Secret) 令牌。
    算法逻辑: MD5(salt = 固定盐值 & t = 当前时间戳 & r = 6位随机字符串)
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
    # 检索宿主机环境变量中的核心凭证
    cookie_credential = os.environ.get("MIHOYO_COOKIE")
    if not cookie_credential:
        print("[核心错误] 未在系统环境中检测到 MIHOYO_COOKIE 凭证，进程强制终止。", file=sys.stderr)
        sys.exit(1)

    # 构造符合米游社移动端协议的安全请求头
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
        
        # 发起高可靠性的同步网络请求，设置 15 秒超时时限
        index_response = requests.get(index_api_url, headers=request_headers, timeout=15).json()
        note_response = requests.get(note_api_url, headers=request_headers, timeout=15).json()
        
        # 验证米游社网关业务状态码 (retcode === 0 表示请求合法且成功)
        if index_response.get("retcode") != 0 or note_response.get("retcode") != 0:
            print(f"[网关拒绝] 接口响应异常。Index_Msg: {index_response.get('message')}, Note_Msg: {note_response.get('message')}", file=sys.stderr)
            sys.exit(1)
            
        raw_stats = index_response["data"]["stats"]
        raw_note = note_response["data"]
        
        # 构造高鲁棒性双层数据模型（向下兼容历史嵌套结构，向上提供一阶平铺字段）
        structured_dataset = {
            # 兼容架构层 1: 完整映射原生命名空间
            "stats": raw_stats,
            "daily_note": raw_note,
            
            # 兼容架构层 2: 平铺核心业务指标，消除前端解析中的多级嵌套依赖
            "days": raw_stats.get("active_day_number"),
            "abyss": raw_stats.get("spiral_abyss"),
            "achievements": raw_stats.get("achievement_number"),
            "characters": raw_stats.get("avatar_number"),
            "resin": raw_note.get("current_resin"),
            "max_resin": raw_note.get("max_resin"),
            "coin": raw_note.get("current_home_coin"),
            "task": raw_note.get("total_task_num", 4) - raw_note.get("finished_task_num", 0),
            "expeditions": f"{sum(1 for item in raw_note.get('expeditions', []) if item.get('status') == 'Finished')}/{raw_note.get('max_expedition_num', 5)}"
        }
        
        # 执行磁盘 IO 原子化写入
        with open("data.json", "w", encoding="utf-8") as file_handle:
            json.dump(structured_dataset, file_handle, ensure_ascii=False, indent=4)
        print("[执行成功] 数据流处理完成，已成功覆盖 data.json 静态数据源。")
            
    except Exception as runtime_error:
        print(f"[系统异常] 运行时发生未捕获的严重错误: {str(runtime_error)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    execute_data_ingestion()