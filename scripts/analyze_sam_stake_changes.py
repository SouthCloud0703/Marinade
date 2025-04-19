#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pytz
import requests
import pandas as pd
import glob
import os

def read_dashboard_data(file_path):
    """ダッシュボードデータを読み込む"""
    data = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    for line in lines[2:]:  # ヘッダーとセパレータをスキップ
        try:
            # 行を|で分割し、各要素の空白を削除
            parts = [p.strip() for p in line.split('|') if p.strip()]
            if len(parts) >= 8:  # 必要な列数があることを確認
                vote_account = parts[1]
                current_commission = float(parts[2].replace('%', ''))
                max_commission = float(parts[3].replace('%', '')) if parts[3] != '-' else 0.0
                
                # 数値データの処理
                def parse_number(value):
                    value = value.replace(',', '')  # カンマを削除
                    try:
                        if value == '∞':
                            return float('inf')
                        return float(value)
                    except ValueError:
                        return 0.0

                sam_stake = parse_number(parts[4])
                bond = parse_number(parts[5])
                total_stake = parse_number(parts[6])
                vote_credits = int(parse_number(parts[7]))
                bid = parse_number(parts[4])  # SAM stakeと同じ
                
                data.append({
                    'vote_account': vote_account,
                    'current_commission': current_commission,
                    'max_commission': max_commission,
                    'sam_stake': sam_stake,
                    'bond': bond,
                    'total_stake': total_stake,
                    'vote_credits': vote_credits,
                    'bid': bid,
                    'marinade_active_stake': 0.0  # 初期値として0.0を設定
                })
        except Exception as e:
            continue
            
    return pd.DataFrame(data)

def get_latest_auction_data():
    """最新のauctionsフォルダからデータを取得"""
    # auctionsフォルダ内の最新のディレクトリを探す
    auction_dirs = glob.glob('auctions/*')
    if not auction_dirs:
        return None
    
    latest_dir = max(auction_dirs, key=os.path.basename)
    results_file = os.path.join(latest_dir, 'outputs/results.json')
    
    if not os.path.exists(results_file):
        return None
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # バリデーターごとのMarinade Active Stakeを抽出
    validator_stakes = {}
    for entry in data:
        if 'voteAccount' in entry and 'totalActivatedStakeSol' in entry:
            validator_stakes[entry['voteAccount']] = float(entry['totalActivatedStakeSol'])
    
    return validator_stakes

def generate_markdown_summary(df, validator_stakes):
    """Markdownサマリーを生成"""
    # JSTでの実行時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    
    # バリデーターステークを追加
    df['marinade_active_stake'] = df['vote_account'].map(lambda x: validator_stakes.get(x, 0))
    
    # サマリー統計を計算
    total_bond = df['bond'].sum()
    total_sam_stake = df['sam_stake'].sum()
    total_active_stake = df['marinade_active_stake'].sum()
    
    markdown = f"""# SAMステーク分析

実行日時: {now.strftime("%Y-%m-%d %H:%M:%S JST")}

## サマリー
- 総ボンド残高: {total_bond:.2f} SOL
- 総SAMステーク: {total_sam_stake:.2f} SOL
- 総Marinade Active Stake: {total_active_stake:.2f} SOL

## バリデーター詳細

| Vote Account | Bid | Bond (SOL) | SAM Stake (SOL) | Marinade Active Stake (SOL) |
|-------------|-----|------------|----------------|---------------------------|
"""
    
    # データを並び替えてバリデーターごとの詳細を追加
    sorted_df = df.sort_values('bond', ascending=False)
    for _, row in sorted_df.iterrows():
        markdown += f"| {row['vote_account']} | {row['bid']:.3f} | {row['bond']:.2f} | {row['sam_stake']:.2f} | {row['marinade_active_stake']:.2f} |\n"

    return markdown

def main():
    """メイン処理"""
    # ダッシュボードデータを読み込む
    dashboard_data = read_dashboard_data('dashboard.md')
    print("Columns:", dashboard_data.columns)
    print("\nFirst few rows:")
    print(dashboard_data.head())
    
    # 最新のオークションデータを取得
    validator_stakes = get_latest_auction_data()
    if validator_stakes is None:
        print("最新のオークションデータの取得に失敗しました。")
        return
    
    # Markdownサマリーを生成
    summary = generate_markdown_summary(dashboard_data, validator_stakes)
    
    # 結果をファイルに保存
    output_dir = Path('analysis_results')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'sam_stake_analysis.md'
    with open(output_file, 'w') as f:
        f.write(summary)
    
    print(f"分析が完了し、結果が{output_file}に保存されました。")

if __name__ == "__main__":
    main() 