#!/usr/bin/env python3
"""
扫描动量股票
筛选标准：涨幅、量比、主力净流入、技术形态
"""

import json
import sys

def scan_momentum_stocks(top_n=20):
    try:
        import akshare as ak
        import pandas as pd
    except ImportError:
        print("错误：请先安装 akshare: pip3 install akshare", file=sys.stderr)
        sys.exit(1)
    
    candidates = []
    
    try:
        # 1. 获取涨幅榜
        print("正在扫描涨幅榜...", file=sys.stderr)
        df = ak.stock_zh_a_spot_em()
        
        # 过滤条件
        # - 涨幅 > 3%（有动量）
        # - 成交额 > 1亿（有流动性）
        # - 排除ST、新股
        df_filtered = df[
            (df['涨跌幅'] > 3) & 
            (df['成交额'] > 100000000) &
            (~df['名称'].str.contains('ST|N|C', na=False))
        ].copy()
        
        # 按涨幅排序
        df_filtered = df_filtered.sort_values('涨跌幅', ascending=False)
        
        # 取前 top_n
        for _, row in df_filtered.head(top_n).iterrows():
            stock = {
                "code": row['代码'],
                "name": row['名称'],
                "price": float(row['最新价']),
                "change_pct": float(row['涨跌幅']),
                "amount": float(row['成交额']),
                "volume_ratio": float(row.get('量比', 0)) if '量比' in row else None,
                "turnover_rate": float(row.get('换手率', 0)) if '换手率' in row else None,
                "sector": row.get('所属行业', '未知') if '所属行业' in row else '未知'
            }
            candidates.append(stock)
        
        # 2. 尝试获取主力资金流向（如果可用）
        try:
            print("正在获取主力资金流向...", file=sys.stderr)
            flow_df = ak.stock_individual_fund_flow_rank(indicator="今日")
            for stock in candidates:
                match = flow_df[flow_df['代码'] == stock['code']]
                if not match.empty:
                    stock['main_net_inflow'] = float(match['主力净流入'].values[0]) if '主力净流入' in match.columns else 0
        except Exception as e:
            print(f"获取主力资金失败: {e}", file=sys.stderr)
        
    except Exception as e:
        print(f"扫描动量股票失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    return candidates

if __name__ == "__main__":
    data = scan_momentum_stocks()
    print(json.dumps(data, ensure_ascii=False, indent=2))
