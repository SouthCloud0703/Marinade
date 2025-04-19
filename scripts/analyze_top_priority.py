import pandas as pd
import os
from argparse import ArgumentParser

def analyze_top_priority(target_epoch):
    # CSVファイルの読み込み
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'epoch_755_to_latest_analysis.csv')
    df = pd.read_csv(csv_path)
    
    # エポック番号を数値型に変換
    df['epoch'] = pd.to_numeric(df['epoch'])
    
    # 指定エポックのデータを抽出
    current_epoch_data = df[df['epoch'] == target_epoch].copy()
    next_epoch_data = df[df['epoch'] == target_epoch + 1].copy() if target_epoch + 1 in df['epoch'].values else None
    
    if len(current_epoch_data) == 0:
        print(f"エポック {target_epoch} のデータが見つかりません。")
        return
    
    if next_epoch_data is None:
        print(f"エポック {target_epoch + 1} のデータが見つかりません。")
        return
    
    # Stake Priorityが1から30のバリデータを抽出
    top_validators = current_epoch_data[
        (current_epoch_data['stake_priority'] >= 1) & 
        (current_epoch_data['stake_priority'] <= 30)
    ].sort_values('stake_priority')
    
    # マークダウンファイルのパス
    md_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', f'top_priority_epoch_{target_epoch}.md')
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Stake Priority Top 30 Validators (Epoch {target_epoch})\n\n")
        
        # ヘッダー行
        f.write("順位 | バリデータ | marinade_activated_stake_sol | marinade_sam_target_sol | bond_balance_sol | bid_pmpe | stake_priority | 次エポックでの増加量\n")
        f.write("--- | --- | --- | --- | --- | --- | --- | ---\n")
        
        # 各バリデータのデータを表示
        for i, (_, row) in enumerate(top_validators.iterrows(), 1):
            # 次のエポックでのステーク量を取得
            next_stake = next_epoch_data[
                next_epoch_data['vote_account'] == row['vote_account']
            ]['marinade_activated_stake_sol'].iloc[0] if len(
                next_epoch_data[next_epoch_data['vote_account'] == row['vote_account']]
            ) > 0 else row['marinade_activated_stake_sol']
            
            # ステーク増加量を計算
            stake_increase = next_stake - row['marinade_activated_stake_sol']
            
            # データ行を作成
            values = [
                str(i),
                row['vote_account'],
                f"{row['marinade_activated_stake_sol']:,.2f}",
                f"{row['marinade_sam_target_sol']:,.2f}",
                f"{row['bond_balance_sol']:,.2f}" if pd.notna(row['bond_balance_sol']) else "-",
                f"{row['bid_pmpe']:.3f}",
                str(int(row['stake_priority'])),
                f"{stake_increase:+,.2f}"
            ]
            
            f.write(" | ".join(values) + "\n")
        
        # サマリー情報
        f.write(f"\n## サマリー\n")
        f.write(f"- 分析対象エポック: {target_epoch}\n")
        f.write(f"- 次エポック: {target_epoch + 1}\n")
        f.write(f"- 対象バリデータの合計ステーク量: {top_validators['marinade_activated_stake_sol'].sum():,.2f} SOL\n")
        f.write(f"- 対象バリデータの平均stake_priority: {top_validators['stake_priority'].mean():.1f}\n")
        f.write(f"- 対象バリデータの平均bid_pmpe: {top_validators['bid_pmpe'].mean():.3f}\n")
    
    print(f"分析レポートを保存しました: {md_path}")

def main():
    parser = ArgumentParser(description='Stake Priorityが1から30のバリデータを分析します')
    parser.add_argument('epoch', type=int, help='分析対象のエポック番号')
    args = parser.parse_args()
    
    analyze_top_priority(args.epoch)

if __name__ == "__main__":
    main() 