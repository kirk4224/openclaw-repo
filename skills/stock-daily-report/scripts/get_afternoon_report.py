#!/usr/bin/env python3
"""
下午跟踪报告数据获取
包含：观察名单复盘、自选股收盘情况、大盘收评
"""

import json
import sys
import requests
from datetime import datetime

def get_stock_data(codes):
    """从新浪财经获取股票数据"""
    # 构建股票代码列表
    code_list = []
    for code in codes:
        if code.startswith('6'):
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
    import re
    results = {}
    
    for line in text.split('\n'):
        if not line.strip():
            continue
        
        # 提取股票代码
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

def get_market_overview():
    """获取大盘指数数据"""
    url = 'https://hq.sinajs.cn/list=sh000001,sz399001,sz399006'
    headers = {'Referer': 'https://finance.sina.com.cn'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        text = response.text
        
        import re
        indices = {}
        
        index_map = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指'
        }
        
        for line in text.split('\n'):
            if not line.strip():
                continue
            
            match = re.match(r'var hq_str_(\w+)="(.*)";', line)
            if not match:
                continue
            
            prefix = match.group(1)
            data = match.group(2)
            
            if prefix not in index_map or not data:
                continue
            
            parts = data.split(',')
            if len(parts) < 10:
                continue
            
            try:
                indices[index_map[prefix]] = {
                    'open': float(parts[1]),
                    'last_close': float(parts[2]),
                    'price': float(parts[3]),
                    'high': float(parts[4]),
                    'low': float(parts[5]),
                    'volume': int(parts[8]),
                    'amount': float(parts[9])
                }
                
                if indices[index_map[prefix]]['last_close'] > 0:
                    indices[index_map[prefix]]['change_pct'] = round(
                        (indices[index_map[prefix]]['price'] - indices[index_map[prefix]]['last_close']) 
                        / indices[index_map[prefix]]['last_close'] * 100, 2
                    )
                else:
                    indices[index_map[prefix]]['change_pct'] = 0
                    
            except (ValueError, IndexError):
                continue
        
        return indices
        
    except Exception as e:
        print(f"获取大盘数据失败: {e}", file=sys.stderr)
        return {}

def get_afternoon_report():
    """生成下午报告数据"""
    
    # 读取自选股列表
    my_stocks = []
    try:
        with open('references/my-stocks.md', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split()
                    if parts:
                        my_stocks.append(parts[0])
    except FileNotFoundError:
        print("未找到自选股列表文件", file=sys.stderr)
    
    # 获取自选股数据
    my_stocks_data = {}
    if my_stocks:
        text = get_stock_data(my_stocks)
        if text:
            my_stocks_data = parse_stock_data(text, my_stocks)
    
    # 获取大盘数据
    market_data = get_market_overview()
    
    result = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'my_stocks': my_stocks_data,
        'market': market_data
    }
    
    return result

if __name__ == "__main__":
    data = get_afternoon_report()
    print(json.dumps(data, ensure_ascii=False, indent=2))
