#!/usr/bin/env python3
"""
获取观察名单股票的收盘数据
"""

import json
import sys
import requests
import re
from datetime import datetime

def get_stock_data(codes):
    """从新浪财经获取股票数据"""
    code_list = []
    for code in codes:
        if (str(code).startswith('6')) or (str(code).startswith('5')):
            code_list.append(f'sh{code}')
        else:
            code_list.append(f'sz{code}')
    
    url = f"https://hq.sinajs.cn/list={','.join(code_list)}"
    headers = {'Referer': 'https://finance.sina.com.cn'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.text
    except Exception as e:
        print(f"获取数据失败: {e}", file=sys.stderr)
        return None

def parse_stock_data(text, codes):
    """解析股票数据"""
    results = {}
    
    for line in text.split('\n'):
        if not line.strip():
            continue
        
        match = re.match(r'var hq_str_(sh|sz)(\d+)="(.*)";', line)
        if not match:
            continue
        
        prefix = match.group(1)
        code = match.group(2)
        data = match.group(3)
        
        if not data:
            continue
        
        parts = data.split(',')
        if len(parts) < 32:
            continue
        
        try:
            stock_info = {
                'code': code,
                'name': parts[0],
                'open': float(parts[1]),
                'last_close': float(parts[2]),
                'price': float(parts[3]),
                'high': float(parts[4]),
                'low': float(parts[5]),
                'volume': int(parts[8]),
                'amount': float(parts[9]),
                'date': parts[30],
                'time': parts[31]
            }
            
            # 计算涨跌幅
            if stock_info['last_close'] > 0:
                stock_info['change_pct'] = round(
                    (stock_info['price'] - stock_info['last_close']) / stock_info['last_close'] * 100, 2
                )
            else:
                stock_info['change_pct'] = 0
            
            results[code] = stock_info
        except (ValueError, IndexError) as e:
            continue
    
    return results

if __name__ == "__main__":
    # 观察名单股票代码
    watchlist_codes = ['600036', '601888', '000858', '002594', '600900']
    
    text = get_stock_data(watchlist_codes)
    if text:
        data = parse_stock_data(text, watchlist_codes)
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("{}", file=sys.stderr)
