#!/usr/bin/env python3
"""
获取A股市场概况
包含：大盘指数、涨跌停统计、成交额、北向资金
"""

import json
import sys

def get_market_overview():
    try:
        import akshare as ak
    except ImportError:
        print("错误：请先安装 akshare: pip3 install akshare", file=sys.stderr)
        sys.exit(1)
    
    result = {
        "indices": {},
        "market_stats": {},
        "north_money": None,
        "timestamp": None
    }
    
    try:
        # 1. 获取实时行情数据
        print("正在获取大盘指数...", file=sys.stderr)
        df = ak.stock_zh_a_spot_em()
        
        # 主要指数代码
        index_map = {
            "000001": "上证指数",
            "399001": "深证成指", 
            "399006": "创业板指"
        }
        
        for code, name in index_map.items():
            row = df[df['代码'] == code]
            if not row.empty:
                result["indices"][name] = {
                    "code": code,
                    "price": float(row['最新价'].values[0]),
                    "change_pct": float(row['涨跌幅'].values[0]),
                    "volume": float(row['成交量'].values[0]),
                    "amount": float(row['成交额'].values[0])
                }
        
        # 2. 统计涨跌停
        print("正在统计涨跌停...", file=sys.stderr)
        up_limit = len(df[df['涨跌幅'] >= 9.9])  # 涨停（近似）
        down_limit = len(df[df['涨跌幅'] <= -9.9])  # 跌停（近似）
        up_count = len(df[df['涨跌幅'] > 0])
        down_count = len(df[df['涨跌幅'] < 0])
        
        result["market_stats"] = {
            "up_limit": up_limit,
            "down_limit": down_limit,
            "up_count": up_count,
            "down_count": down_count,
            "total": len(df)
        }
        
        # 3. 北向资金（如果有）
        try:
            print("正在获取北向资金...", file=sys.stderr)
            north_df = ak.stock_hsgt_north_net_flow_in_em()
            if not north_df.empty:
                latest = north_df.iloc[-1]
                result["north_money"] = {
                    "date": str(latest['日期']),
                    "net_flow": float(latest['当日净流入']) if '当日净流入' in latest else 0
                }
        except Exception as e:
            print(f"获取北向资金失败: {e}", file=sys.stderr)
        
        from datetime import datetime
        result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        print(f"获取市场数据失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    return result

if __name__ == "__main__":
    data = get_market_overview()
    print(json.dumps(data, ensure_ascii=False, indent=2))
