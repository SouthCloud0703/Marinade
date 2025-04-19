#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pytz
import requests

def fetch_validator_info(vote_account):
    """バリデータ情報を取得"""
    url = f"https://validators-api.marinade.finance/v1/validators/{vote_account}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None

def fetch_sam_auction_data():
    """SAMオークションデータを取得"""
    url = "https://validator-bonds-api.marinade.finance/v1/sam/current"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"APIからのデータ取得に失敗しました: {e}")
        return None

def format_value(value, decimal_places=2):
    """数値を指定された小数点以下の桁数でフォーマット。Noneの場合は'-'を返す"""
    if value is None:
        return '-'
    return f"{float(value):.{decimal_places}f}"

def generate_markdown_summary(data):
    """Markdownサマリーを生成"""
    if not data:
        return "データの取得に失敗しました。"

    # JSTでの実行時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    
    # バリデーターデータを抽出（ボンドを持つものだけ）
    validators = [v for v in data['auctionData'] if v.get('bondBalanceSol', 0) > 0]
    
    # 合計値を計算
    total_bond = sum(float(v.get('bondBalanceSol', 0)) for v in validators)
    total_sam_stake = sum(float(v.get('auctionStake', {}).get('marinadeSamTargetSol', 0)) for v in validators)
    
    # Markdownを生成
    markdown = f"""# SAMオークションステータス

実行日時: {now.strftime("%Y-%m-%d %H:%M:%S JST")}

## サマリー
- 参加バリデーター数: {len(validators)}
- 総ボンド残高: {total_bond:.2f} SOL
- 総SAMステーク: {total_sam_stake:.2f} SOL

## バリデーター詳細

| Vote Account | Bond (SOL) | Bid (per 1000 SOL) | SAM Stake (SOL) |
|-------------|------------|-------------------|----------------|
"""
    
    # バリデーターごとの詳細を追加
    for v in sorted(validators, key=lambda x: float(x.get('bondBalanceSol', 0)), reverse=True):
        vote_account = v.get('voteAccount', 'N/A')
        bond_balance = float(v.get('bondBalanceSol', 0))
        bid = float(v.get('revShare', {}).get('bidPmpe', 0))
        sam_stake = float(v.get('auctionStake', {}).get('marinadeSamTargetSol', 0))
        
        markdown += f"| {vote_account} | {bond_balance:.2f} | {bid:.2f} | {sam_stake:.2f} |\n"

    return markdown

def main():
    """メイン処理"""
    # データを取得
    data = fetch_sam_auction_data()
    
    # Markdownサマリーを生成
    summary = generate_markdown_summary(data)
    
    # 結果をファイルに保存
    output_dir = Path('analysis_results')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'sam_status.md', 'w') as f:
        f.write(summary)
    
    print("分析が完了し、結果がanalysis_results/sam_status.mdに保存されました。")

if __name__ == "__main__":
    main() 