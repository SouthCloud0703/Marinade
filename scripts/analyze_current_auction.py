#!/usr/bin/env python3

import os
import json
from datetime import datetime
import pandas as pd

def get_latest_epoch():
    """最新のエポックフォルダを取得"""
    auctions_dir = "auctions"
    epochs = [d for d in os.listdir(auctions_dir) if not d.startswith('.')]
    if not epochs:
        raise ValueError("オークションデータが見つかりません")
    return sorted(epochs)[-1].split('.')[0]

def load_auction_data(epoch):
    """指定されたエポックのオークションデータを読み込む"""
    auction_files = [f for f in os.listdir(f"auctions/{epoch}.*") if f.endswith('.json')]
    if not auction_files:
        raise ValueError(f"エポック {epoch} のオークションデータが見つかりません")
    
    latest_file = sorted(auction_files)[-1]
    with open(f"auctions/{epoch}.{latest_file}", 'r') as f:
        return json.load(f)

def analyze_current_auction(epoch):
    """現在のオークションの参加者とbidを分析"""
    data = load_auction_data(epoch)
    
    # バリデータごとのbid情報を収集
    bids = []
    for validator in data['validators']:
        if validator.get('marinadeBid'):
            bids.append({
                'validator': validator['vote_address'],
                'bid': validator['marinadeBid'],
                'stake': validator.get('activatedStake', 0),
                'commission': validator.get('commission', 0)
            })
    
    # DataFrameを作成して並び替え
    df = pd.DataFrame(bids)
    df = df.sort_values('bid', ascending=False)
    
    return df

def generate_markdown_report(df, epoch):
    """分析結果をMarkdownレポートとして生成"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S JST')
    
    report = f"""# 現在のオークション参加状況
実行時刻: {now}
エポック: {epoch}

## オークション参加バリデータ一覧
全参加数: {len(df)} バリデータ

| バリデータ | Bid (SOL) | Stake (SOL) | Commission (%) |
|------------|-----------|-------------|----------------|
"""
    
    for _, row in df.iterrows():
        report += f"| {row['validator']} | {row['bid']:,.2f} | {row['stake']/1e9:,.2f} | {row['commission']} |\n"
    
    return report

def main():
    # 最新のエポックを取得
    epoch = get_latest_epoch()
    
    # オークションデータを分析
    df = analyze_current_auction(epoch)
    
    # レポートを生成
    report = generate_markdown_report(df, epoch)
    
    # 結果を保存
    os.makedirs('analysis_results', exist_ok=True)
    output_file = f'analysis_results/current_auction_epoch_{epoch}.md'
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"分析結果を {output_file} に保存しました")

if __name__ == '__main__':
    main() 