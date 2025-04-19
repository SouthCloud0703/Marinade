import pandas as pd
import os
from argparse import ArgumentParser

def analyze_rebalance(target_epoch=None):
    # CSVファイルの読み込み
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'epoch_755_to_latest_analysis.csv')
    df = pd.read_csv(csv_path)
    
    # エポック番号の降順でソート
    df['epoch'] = pd.to_numeric(df['epoch'])
    df = df.sort_values('epoch', ascending=False)
    
    # 特定のエポックが指定された場合、そのエポックのデータのみを分析
    if target_epoch is not None:
        df = df[df['epoch'] == target_epoch]
        if len(df) == 0:
            print(f"エポック {target_epoch} のデータが見つかりません。")
            return
    
    # エポックごとの集計
    results = []
    for epoch in df['epoch'].unique():
        epoch_data = df[df['epoch'] == epoch]
        
        # リバランス量の計算
        rebalance_data = {
            'epoch': epoch,
            'total_target': epoch_data['marinade_sam_target_sol'].sum(),
            'total_activated': epoch_data['marinade_activated_stake_sol'].sum(),
            'validator_count': len(epoch_data),
            'active_validator_count': len(epoch_data[epoch_data['marinade_activated_stake_sol'] > 0]),
            'target_validator_count': len(epoch_data[epoch_data['marinade_sam_target_sol'] > 0])
        }
        
        # リバランス必要量（絶対値の合計）
        rebalance_data['total_rebalance_abs'] = abs(
            epoch_data['marinade_sam_target_sol'] - epoch_data['marinade_activated_stake_sol']
        ).sum()
        
        # プラスのリバランス（追加ステーク）が必要なバリデータ
        positive_rebalance = epoch_data[
            epoch_data['marinade_sam_target_sol'] > epoch_data['marinade_activated_stake_sol']
        ]
        rebalance_data['positive_rebalance'] = (
            positive_rebalance['marinade_sam_target_sol'] - 
            positive_rebalance['marinade_activated_stake_sol']
        ).sum()
        rebalance_data['positive_validator_count'] = len(positive_rebalance)
        
        # マイナスのリバランス（引き出し）が必要なバリデータ
        negative_rebalance = epoch_data[
            epoch_data['marinade_sam_target_sol'] < epoch_data['marinade_activated_stake_sol']
        ]
        rebalance_data['negative_rebalance'] = (
            negative_rebalance['marinade_sam_target_sol'] - 
            negative_rebalance['marinade_activated_stake_sol']
        ).sum()
        rebalance_data['negative_validator_count'] = len(negative_rebalance)
        
        results.append(rebalance_data)
    
    # 結果をDataFrameに変換
    results_df = pd.DataFrame(results)
    
    # マークダウンファイルのパス
    md_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'rebalance_analysis.md')
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# Rebalance Analysis Report\n\n")
        
        latest_epoch = results_df['epoch'].max()
        latest_data = results_df[results_df['epoch'] == latest_epoch].iloc[0]
        
        # 最新エポックのサマリー
        f.write(f"## エポック {int(latest_epoch)} のサマリー\n")
        f.write(f"- 総ターゲットステーク量: {latest_data['total_target']:,.2f} SOL\n")
        f.write(f"- 総アクティブステーク量: {latest_data['total_activated']:,.2f} SOL\n")
        f.write(f"- 総リバランス必要量: {latest_data['total_rebalance_abs']:,.2f} SOL\n")
        f.write(f"- ステーク追加が必要: {latest_data['positive_rebalance']:,.2f} SOL（{int(latest_data['positive_validator_count'])}バリデータ）\n")
        f.write(f"- ステーク引き出しが必要: {abs(latest_data['negative_rebalance']):,.2f} SOL（{int(latest_data['negative_validator_count'])}バリデータ）\n")
        f.write(f"- 総バリデータ数: {int(latest_data['validator_count'])}\n")
        f.write(f"- アクティブステークありバリデータ数: {int(latest_data['active_validator_count'])}\n")
        f.write(f"- ターゲットステークありバリデータ数: {int(latest_data['target_validator_count'])}\n\n")
        
        if target_epoch is None:
            # エポックごとの推移（単一エポックの場合は表示しない）
            f.write("## エポックごとの推移\n")
            f.write("エポック | 総ターゲット | 総アクティブ | リバランス必要量 | 追加必要量 | 引き出し必要量 | 総バリデータ数 | アクティブ数 | ターゲット数\n")
            f.write("--- | --- | --- | --- | --- | --- | --- | --- | ---\n")
            
            for _, row in results_df.iterrows():
                f.write(
                    f"E{int(row['epoch'])} | "
                    f"{row['total_target']:,.2f} | "
                    f"{row['total_activated']:,.2f} | "
                    f"{row['total_rebalance_abs']:,.2f} | "
                    f"{row['positive_rebalance']:,.2f} | "
                    f"{abs(row['negative_rebalance']):,.2f} | "
                    f"{int(row['validator_count'])} | "
                    f"{int(row['active_validator_count'])} | "
                    f"{int(row['target_validator_count'])}\n"
                )
    
    print(f"分析レポートを保存しました: {md_path}")

def main():
    parser = ArgumentParser(description='リバランス分析を実行します')
    parser.add_argument('--epoch', type=int, help='分析対象の特定のエポック番号')
    args = parser.parse_args()
    
    analyze_rebalance(args.epoch)

if __name__ == "__main__":
    main() 