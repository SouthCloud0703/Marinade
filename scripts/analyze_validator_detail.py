import pandas as pd
import os
from argparse import ArgumentParser

def analyze_validator_detail(vote_account):
    # CSVファイルの読み込み
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'analysis_results', 'epoch_755_to_latest_analysis.csv')
    df = pd.read_csv(csv_path)
    
    # エポック番号の降順でソート
    df['epoch'] = pd.to_numeric(df['epoch'])
    df = df.sort_values('epoch', ascending=False)
    
    # 指定されたバリデータのデータを抽出
    validator_data = df[df['vote_account'] == vote_account].copy()
    
    if len(validator_data) == 0:
        print(f"バリデータ {vote_account} のデータが見つかりません。")
        return
    
    # 最新のエポックを取得
    latest_epoch = validator_data['epoch'].max()
    oldest_epoch = max(latest_epoch - 29, validator_data['epoch'].min())  # 直近30エポック分
    
    # 分析対象の指標
    metrics = [
        'marinade_activated_stake_sol',
        'marinade_sam_target_sol',
        'bond_balance_sol',
        'bid_pmpe',
        'stake_priority',
        'unstake_priority'
    ]
    
    # マークダウンファイルのパス
    script_dir = os.path.dirname(__file__)
    output_file = os.path.join(script_dir, '..', 'analysis_results', f'validator_detail_{vote_account}.md')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Validator Detail Analysis: {vote_account}\n\n")
        
        # ヘッダー行
        f.write("エポック | marinade_activated_stake_sol | marinade_sam_target_sol | bond_balance_sol | bid_pmpe | stake_priority | unstake_priority\n")
        f.write("--- | --- | --- | --- | --- | --- | ---\n")
        
        # 対象期間のデータを抽出
        target_data = validator_data[
            (validator_data['epoch'] <= latest_epoch) & 
            (validator_data['epoch'] >= oldest_epoch)
        ].sort_values('epoch', ascending=False)
        
        # 各エポックのデータを表示
        for _, row in target_data.iterrows():
            values = []
            for metric in metrics:
                value = row[metric]
                if pd.notna(value):
                    if metric == 'bid_pmpe':
                        values.append(f"{value:.3f}")
                    elif metric == 'stake_priority':
                        values.append(f"{int(value)}")
                    else:
                        values.append(f"{value:.2f}")
                else:
                    values.append("-")
            
            f.write(f"E{int(row['epoch'])} | {' | '.join(values)}\n")
    
    print(f"分析レポートを保存しました: {output_file}")

def main():
    parser = ArgumentParser(description='指定したバリデータの詳細分析を行います')
    parser.add_argument('vote_account', help='分析対象のvote account')
    args = parser.parse_args()
    
    analyze_validator_detail(args.vote_account)

if __name__ == "__main__":
    main() 