#!/usr/bin/env python3
"""
分析用户自选股
读取 references/my-stocks.md 中的股票代码进行分析
"""

import json
import sys
import os

def load_my_stocks():
    """从配置文件读取自选股列表"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, '..', 'references', 'my-stocks.md')
    
    stocks = []
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                # 格式：股票代码 或 股票代码 股票名称
                parts = line.split()
                if parts:
                    stocks.append({
                        'code': parts[0],
                        'name': parts[1] if len(parts) > 1 else None
                    })
    return stocks

def analyze_stock(code, name=None):
    """分析单只股票"""
    try:
        import akshare as ak
    except ImportError:
        return None
    
    result = {
        'code': code,
        'name': name,
        'price': None,
        'change_pct': None,
        'analysis': None
    }
    
    try:
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        row = df[df['代码'] == code]
        
        if not row.empty:
            result['name'] = row['名称'].values[0]
            result['price'] = float(row['最新价'].values[0])
            result['change_pct'] = float(row['涨跌幅'].values[0])
            result['volume'] = float(row['成交量'].values[0])
            result['amount'] = float(row['成交额'].values[0])
            result['turnover_rate'] = float(row.get('换手率', 0).values[0]) if '换手率' in row else None
            
            # 简单技术分析
            change = result['change_pct']
            if change > 5:
                trend = "强势上涨"
                up_prob = min(75, 55 + change * 2)
            elif change > 2:
                trend = "震荡偏强"
                up_prob = 55 + change * 1.5
            elif change > 0:
                trend = "小幅上涨"
                up_prob = 50 + change
            elif change > -2:
                trend = "小幅下跌"
                up_prob = 50 + change
            elif change > -5:
                trend = "震荡偏弱"
                up_prob = max(25, 50 + change * 1.5)
            else:
                trend = "弱势下跌"
                up_prob = max(15, 50 + change * 2)
            
            result['analysis'] = {
                'trend': trend,
                'up_probability': round(up_prob, 1),
                'down_probability': round(100 - up_prob, 1)
            }
            
    except Exception as e:
        result['error'] = str(e)
    
    return result

def analyze_all_stocks():
    """分析所有自选股"""
    stocks = load_my_stocks()
    
    if not stocks:
        return {
            'error': '未配置自选股，请在 references/my-stocks.md 中添加股票代码',
            'stocks': []
        }
    
    results = []
    for stock in stocks:
        print(f"正在分析 {stock['code']}...", file=sys.stderr)
        result = analyze_stock(stock['code'], stock.get('name'))
        if result:
            results.append(result)
    
    return {
        'count': len(results),
        'stocks': results
    }

if __name__ == "__main__":
    data = analyze_all_stocks()
    print(json.dumps(data, ensure_ascii=False, indent=2))
