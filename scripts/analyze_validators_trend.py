import pandas as pd
import numpy as np
import os
from datetime import datetime

def create_markdown_report(df, latest_epoch):
    # Markdownファイルのパス
    md_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'latest_over200_analysis.md')
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Validator Analysis Report (Epoch {latest_epoch})\n\n")
        
        # 1. バリデータ数
        validator_count = len(df)
        f.write(f"## 1. marinade_activated_stake_sol >= 100,000のバリデータ数\n")
        f.write(f"- 合計: {validator_count}バリデータ\n\n")
        
        # 2. bid分布
        f.write("## 2. bid_pmpe分布\n")
        bid_stats = df['bid_pmpe_epoch_0'].describe()
        f.write(f"- 最小値: {bid_stats['min']:.3f}\n")
        f.write(f"- 最大値: {bid_stats['max']:.3f}\n")
        f.write(f"- 平均値: {bid_stats['mean']:.3f}\n")
        f.write(f"- 中央値: {bid_stats['50%']:.3f}\n\n")
        
        # 3. bond分布
        f.write("## 3. bond_balance_sol分布\n")
        bond_stats = df['bond_balance_sol_epoch_0'].describe()
        f.write(f"- 最小値: {bond_stats['min']:.2f}\n")
        f.write(f"- 最大値: {bond_stats['max']:.2f}\n")
        f.write(f"- 平均値: {bond_stats['mean']:.2f}\n")
        f.write(f"- 中央値: {bond_stats['50%']:.2f}\n\n")
        
        # 4. stake priority分布
        f.write("## 4. stake_priority分布\n")
        stake_stats = df['stake_priority_epoch_0'].describe()
        f.write(f"- 最小値: {stake_stats['min']:.2f}\n")
        f.write(f"- 最大値: {stake_stats['max']:.2f}\n")
        f.write(f"- 平均値: {stake_stats['mean']:.2f}\n")
        f.write(f"- 中央値: {stake_stats['50%']:.2f}\n\n")
        
        # 5. unstake priority分布
        f.write("## 5. unstake_priority分布\n")
        unstake_stats = df['unstake_priority_epoch_0'].describe()
        f.write(f"- 最小値: {unstake_stats['min']:.2f}\n")
        f.write(f"- 最大値: {unstake_stats['max']:.2f}\n")
        f.write(f"- 平均値: {unstake_stats['mean']:.2f}\n")
        f.write(f"- 中央値: {unstake_stats['50%']:.2f}\n\n")
        
        # 6. marinade_activated_stake_sol上位10バリデータ
        f.write("## 6. marinade_activated_stake_sol上位10バリデータ\n")
        top10 = df.nlargest(10, 'marinade_activated_stake_sol_epoch_0')[['vote_account', 'marinade_activated_stake_sol_epoch_0']]
        for _, row in top10.iterrows():
            f.write(f"- name: {row['vote_account']}, marinade_activated_stake_sol: {row['marinade_activated_stake_sol_epoch_0']:.2f} SOL\n")
        f.write("\n")
        
        # 7. Top10バリデータの推移
        f.write("## 7. Top10バリデータの推移\n")
        metrics = ['marinade_activated_stake_sol', 'bid_pmpe', 'bond_balance_sol', 'stake_priority', 'unstake_priority']
        top10_validators = df.nlargest(10, 'marinade_activated_stake_sol_epoch_0')
        
        for _, validator in top10_validators.iterrows():
            f.write(f"### {validator['vote_account']}\n")
            # ヘッダー行
            f.write("エポック | marinade_activated_stake_sol | bid_pmpe | bond_balance_sol | stake_priority | unstake_priority\n")
            f.write("--- | --- | --- | --- | --- | ---\n")
            # 各エポックのデータ
            for i in range(10):
                values = []
                bid_pmpe = validator[f'bid_pmpe_epoch_{i}']
                # bid_pmpeが0または欠損値の場合はスキップ
                if pd.isna(bid_pmpe) or bid_pmpe == 0:
                    continue
                
                for metric in metrics:
                    value = validator[f'{metric}_epoch_{i}']
                    if pd.notna(value):
                        if metric == 'bid_pmpe':
                            values.append(f"{value:.3f}")
                        else:
                            values.append(f"{value:.2f}")
                    else:
                        values.append("-")
                f.write(f"E-{i} | {' | '.join(values)}\n")
            f.write("\n")
    
    print(f"分析レポートを保存しました: {md_path}")

def analyze_validator_trends():
    # CSVファイルの読み込み
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'epoch_755_to_latest_analysis.csv')
    df = pd.read_csv(csv_path)
    
    # エポック番号の降順でソート
    df['epoch'] = pd.to_numeric(df['epoch'])
    df = df.sort_values('epoch', ascending=False)
    
    # 最新のエポックを取得
    latest_epoch = df['epoch'].max()
    
    # 最新エポックでmarinade_activated_stake_solが100,000以上のバリデータを抽出
    latest_validators = df[
        (df['epoch'] == latest_epoch) & 
        (df['marinade_activated_stake_sol'] >= 100000)
    ]['vote_account'].unique()
    
    # 分析対象の指標
    metrics = [
        'marinade_activated_stake_sol',
        'bid_pmpe',
        'bond_balance_sol',
        'stake_priority',
        'unstake_priority'
    ]
    
    # 各バリデータの直近10エポック分のデータを取得
    results = []
    for validator in latest_validators:
        validator_data = df[df['vote_account'] == validator].sort_values('epoch', ascending=False).head(10)
        
        # バリデータの基本情報を取得
        latest_data = validator_data.iloc[0]
        base_info = {
            'vote_account': validator,
            'name': latest_data['aso']
        }
        
        # 各指標の推移を取得
        for metric in metrics:
            values = validator_data[metric].tolist()
            # 不足分は None で埋める
            values.extend([None] * (10 - len(values)))
            for i, value in enumerate(values):
                base_info[f'{metric}_epoch_{i}'] = value
        
        results.append(base_info)
    
    # 結果をDataFrameに変換
    results_df = pd.DataFrame(results)
    
    # CSVファイルとして保存
    output_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'latest_over200.csv')
    results_df.to_csv(output_path, index=False)
    print(f"分析結果を保存しました: {output_path}")
    
    # Markdownレポートを生成
    create_markdown_report(results_df, latest_epoch)

if __name__ == "__main__":
    analyze_validator_trends() 