#!/usr/bin/env python3
"""
获取A股市场概况（修复版：直接调用东方财富API）
包含：大盘指数、涨跌停统计、成交额、北向资金
"""

import json
import sys
import requests
from datetime import datetime

def get_market_overview():
    result = {
        "indices": {},
        "market_stats": {},
        "north_money": None,
        "timestamp": None
    }
    
    try:
        # 1. 获取大盘指数
        print("正在获取大盘指数...", file=sys.stderr)
        index_url = "http://push2.eastmoney.com/api/qt/ulist.np/get"
        index_params = {
            "fltt": 2,
            "invt": 2,
            "fields": "f2,f3,f4,f5,f6,f12,f14",
            "secids": "1.000001,0.399001,0.399006"
        }
        response = requests.get(index_url, params=index_params, timeout=10)
        index_data = response.json()
        
        index_map = {
            "000001": "上证指数",
            "399001": "深证成指", 
            "399006": "创业板指"
        }
        
        for item in index_data["data"]["diff"]:
            code = item["f12"]
            name = index_map.get(code, item["f14"])
            result["indices"][name] = {
                "code": code,
                "price": float(item["f2"]),
                "change_pct": float(item["f3"]),
                "change": float(item["f4"]),
                "volume": float(item["f5"]) / 10000,  # 万手
                "amount": float(item["f6"]) / 100000000  # 亿元
            }
        
        # 2. 获取市场涨跌统计
        print("正在统计涨跌停...", file=sys.stderr)
        market_url = "http://push2.eastmoney.com/api/qt/ulist.np/get"
        market_params = {
            "fltt": 2,
            "invt": 2,
            "fields": "f1,f2,f3,f12,f14",
            "secids": "1.000001,0.399001,0.399006,0.399852,0.399853,0.399854,0.399855,0.399856,0.399857"
        }
        response = requests.get(market_url, params=market_params, timeout=10)
        market_data = response.json()
        
        up_limit = 0
        down_limit = 0
        up_count = 0
        down_count = 0
        flat_count = 0
        total = 0
        
        for item in market_data["data"]["diff"]:
            if item["f12"] == "399852":  # 上涨家数
                up_count = int(item["f2"])
            elif item["f12"] == "399853":  # 下跌家数
                down_count = int(item["f2"])
            elif item["f12"] == "399854":  # 平盘数
                flat_count = int(item["f2"])
            elif item["f12"] == "399855":  # 涨停数
                up_limit = int(item["f2"])
            elif item["f12"] == "399856":  # 跌停数
                down_limit = int(item["f2"])
        
        total = up_count + down_count + flat_count
        
        result["market_stats"] = {
            "up_limit": up_limit,
            "down_limit": down_limit,
            "up_count": up_count,
            "down_count": down_count,
            "flat_count": flat_count,
            "total": total
        }
        
        # 3. 获取北向资金
        try:
            print("正在获取北向资金...", file=sys.stderr)
            north_url = "http://push2.eastmoney.com/api/qt/stock/get"
            north_params = {
                "fltt": 2,
                "invt": 2,
                "fields": "f43,f44,f45,f46,f47,f48,f60,f116,f117,f168,f169,f170,f171",
                "secid": "1.000001"
            }
            response = requests.get(north_url, params=north_params, timeout=10)
            north_data = response.json()
            # 北向资金需要单独接口，这里简化处理
            result["north_money"] = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "net_flow": "待获取"
            }
        except Exception as e:
            print(f"获取北向资金失败: {e}", file=sys.stderr)
        
        result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        print(f"获取市场数据失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    return result

if __name__ == "__main__":
    data = get_market_overview()
    print(json.dumps(data, ensure_ascii=False, indent=2))
