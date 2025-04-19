import pandas as pd
import os
from argparse import ArgumentParser
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def analyze_bond_target_relationship(target_epoch):
    # CSVファイルの読み込み
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'epoch_755_to_latest_analysis.csv')
    df = pd.read_csv(csv_path)
    
    # エポック番号を数値型に変換
    df['epoch'] = pd.to_numeric(df['epoch'])
    
    # 指定エポックのデータを抽出
    epoch_data = df[df['epoch'] == target_epoch].copy()
    
    if len(epoch_data) == 0:
        print(f"エポック {target_epoch} のデータが見つかりません。")
        return
    
    # bond_balance_solとmarinade_sam_target_solの両方が0より大きいデータのみを抽出
    valid_data = epoch_data[
        (epoch_data['bond_balance_sol'] > 0) & 
        (epoch_data['marinade_sam_target_sol'] > 0)
    ].copy()
    
    # 相関係数を計算
    correlation = valid_data['bond_balance_sol'].corr(valid_data['marinade_sam_target_sol'])
    
    # 散布図を作成
    plt.figure(figsize=(10, 6))
    plt.scatter(valid_data['bond_balance_sol'], valid_data['marinade_sam_target_sol'], alpha=0.5)
    plt.xlabel('Bond Balance (SOL)')
    plt.ylabel('Marinade SAM Target (SOL)')
    plt.title(f'Bond Balance vs Marinade SAM Target (Epoch {target_epoch})')
    
    # 回帰直線を追加
    z = np.polyfit(valid_data['bond_balance_sol'], valid_data['marinade_sam_target_sol'], 1)
    p = np.poly1d(z)
    plt.plot(valid_data['bond_balance_sol'], p(valid_data['bond_balance_sol']), "r--", alpha=0.8)
    
    # グラフを保存
    plot_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', f'bond_target_relationship_{target_epoch}.png')
    plt.savefig(plot_path)
    plt.close()
    
    # 統計情報を計算
    stats_data = {
        'bond_balance_sol': {
            'min': valid_data['bond_balance_sol'].min(),
            'max': valid_data['bond_balance_sol'].max(),
            'mean': valid_data['bond_balance_sol'].mean(),
            'median': valid_data['bond_balance_sol'].median()
        },
        'marinade_sam_target_sol': {
            'min': valid_data['marinade_sam_target_sol'].min(),
            'max': valid_data['marinade_sam_target_sol'].max(),
            'mean': valid_data['marinade_sam_target_sol'].mean(),
            'median': valid_data['marinade_sam_target_sol'].median()
        }
    }
    
    # 分位点でグループ化して分析
    valid_data['bond_quantile'] = pd.qcut(valid_data['bond_balance_sol'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
    quantile_analysis = valid_data.groupby('bond_quantile').agg({
        'bond_balance_sol': ['min', 'max', 'mean', 'count'],
        'marinade_sam_target_sol': ['mean', 'median']
    }).round(2)
    
    # マークダウンファイルのパス
    md_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', f'bond_target_analysis_{target_epoch}.md')
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Bond BalanceとMarinade SAM Targetの関係分析 (Epoch {target_epoch})\n\n")
        
        f.write("## 相関分析\n")
        f.write(f"- 相関係数: {correlation:.3f}\n")
        f.write(f"- 有効なデータ数: {len(valid_data)}\n\n")
        
        f.write("## 基本統計量\n\n")
        f.write("### Bond Balance (SOL)\n")
        f.write(f"- 最小値: {stats_data['bond_balance_sol']['min']:,.2f}\n")
        f.write(f"- 最大値: {stats_data['bond_balance_sol']['max']:,.2f}\n")
        f.write(f"- 平均値: {stats_data['bond_balance_sol']['mean']:,.2f}\n")
        f.write(f"- 中央値: {stats_data['bond_balance_sol']['median']:,.2f}\n\n")
        
        f.write("### Marinade SAM Target (SOL)\n")
        f.write(f"- 最小値: {stats_data['marinade_sam_target_sol']['min']:,.2f}\n")
        f.write(f"- 最大値: {stats_data['marinade_sam_target_sol']['max']:,.2f}\n")
        f.write(f"- 平均値: {stats_data['marinade_sam_target_sol']['mean']:,.2f}\n")
        f.write(f"- 中央値: {stats_data['marinade_sam_target_sol']['median']:,.2f}\n\n")
        
        f.write("## Bond Balance分位点ごとの分析\n\n")
        f.write("分位点 | Bond Balance範囲 | 平均Bond Balance | データ数 | 平均Target | 中央値Target\n")
        f.write("--- | --- | --- | --- | --- | ---\n")
        
        for idx in ['Q1', 'Q2', 'Q3', 'Q4']:
            bond_min = quantile_analysis.loc[idx, ('bond_balance_sol', 'min')]
            bond_max = quantile_analysis.loc[idx, ('bond_balance_sol', 'max')]
            bond_mean = quantile_analysis.loc[idx, ('bond_balance_sol', 'mean')]
            count = quantile_analysis.loc[idx, ('bond_balance_sol', 'count')]
            target_mean = quantile_analysis.loc[idx, ('marinade_sam_target_sol', 'mean')]
            target_median = quantile_analysis.loc[idx, ('marinade_sam_target_sol', 'median')]
            
            f.write(f"{idx} | {bond_min:,.2f} - {bond_max:,.2f} | {bond_mean:,.2f} | {count} | {target_mean:,.2f} | {target_median:,.2f}\n")
        
        f.write(f"\n## 散布図\n")
        f.write(f"散布図は以下のファイルに保存されました：\n")
        f.write(f"- `analysis_results/bond_target_relationship_{target_epoch}.png`\n")
    
    print(f"分析レポートを保存しました: {md_path}")
    print(f"散布図を保存しました: {plot_path}")

def main():
    parser = ArgumentParser(description='Bond BalanceとMarinade SAM Targetの関係を分析します')
    parser.add_argument('epoch', type=int, help='分析対象のエポック番号')
    args = parser.parse_args()
    
    analyze_bond_target_relationship(args.epoch)

if __name__ == "__main__":
    main() 