import pandas as pd
import os
import json
import argparse
from collections import defaultdict

def analyze_stake_by_country(target_epoch=None):
    # CSVファイルを読み込む
    df = pd.read_csv('analysis_results/epoch_755_to_latest_analysis.csv')
    
    # エポックの降順でソート
    df = df.sort_values('epoch', ascending=False)
    
    # 特定のエポックが指定された場合、そのエポックのデータのみを抽出
    if target_epoch is not None:
        df = df[df['epoch'] == target_epoch]
        if df.empty:
            print(f"エポック {target_epoch} のデータが見つかりません。")
            return
    
    # 結果を保存するMarkdownファイル
    output_file = f'analysis_results/stake_by_country{"_" + str(target_epoch) if target_epoch else ""}.md'
    
    # エポックごとの国別ステーク集計
    epoch_country_stats = defaultdict(lambda: defaultdict(float))
    epoch_total_stakes = defaultdict(float)
    
    # データを集計
    for _, row in df.iterrows():
        epoch = row['epoch']
        country = row['country'] if pd.notna(row['country']) else 'Unknown'
        stake = row['marinade_activated_stake_sol']
        
        if pd.notna(stake):
            epoch_country_stats[epoch][country] += stake
            epoch_total_stakes[epoch] += stake
    
    # 結果をMarkdownファイルに書き込む
    with open(output_file, 'w') as f:
        f.write('# Stake Distribution by Country\n\n')
        
        # エポックごとの分析を書き込む
        for epoch in sorted(epoch_country_stats.keys(), reverse=True):
            f.write(f'## Epoch {epoch}\n\n')
            
            # 国ごとのステークと割合を計算
            country_stats = []
            total_stake = epoch_total_stakes[epoch]
            
            for country, stake in epoch_country_stats[epoch].items():
                percentage = (stake / total_stake * 100) if total_stake > 0 else 0
                country_stats.append({
                    'country': country,
                    'stake': stake,
                    'percentage': percentage
                })
            
            # ステーク量で降順ソート
            country_stats.sort(key=lambda x: x['stake'], reverse=True)
            
            # テーブルヘッダー
            f.write('| Country | Stake (SOL) | Share (%) |\n')
            f.write('|---------|-------------|------------|\n')
            
            # 各国のデータを書き込む
            for stat in country_stats:
                f.write(f"| {stat['country']} | {stat['stake']:,.2f} | {stat['percentage']:.2f} |\n")
            
            f.write(f"\nTotal Stake: {total_stake:,.2f} SOL\n\n")
            f.write('---\n\n')
    
    print(f"分析レポートが {output_file} に保存されました。")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='国ごとのステーク分布を分析します')
    parser.add_argument('--epoch', type=int, help='分析対象のエポック番号')
    args = parser.parse_args()
    
    analyze_stake_by_country(args.epoch) 