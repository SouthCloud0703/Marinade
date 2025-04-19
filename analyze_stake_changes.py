#!/usr/bin/env python3
import sys
import json
import pandas as pd
import os
from typing import Dict, List, Tuple
from glob import glob
from pathlib import Path
from datetime import datetime

def ensure_directory_exists(directory):
    """ディレクトリが存在しない場合は作成"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def format_sol(value):
    """SOL値を3桁の小数点で整形"""
    return f"{value:,.3f}"

def generate_markdown_summary(df_stake: pd.DataFrame, df_unstake: pd.DataFrame, epoch: int) -> str:
    """分析結果のMarkdownサマリーを生成"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 合計値の計算
    total_stake_increase = 0
    total_unstake = 0
    
    # ステーク側の合計計算（増加分のみ）
    for _, row in df_stake.iterrows():
        stake_change = row['stakeChange']
        if stake_change > 0:
            total_stake_increase += stake_change
    
    # アンステーク側の合計計算
    for _, row in df_unstake.iterrows():
        stake_change = row['stakeChange']
        total_unstake += abs(stake_change)
    
    markdown = f"""# エポック{epoch}のバリデータ分析結果

## 分析実行日時
{now}

## 全体サマリー
### ステーク優先度上位バリデータ（Priority 1-100）
- 合計増加量: +{format_sol(total_stake_increase)} SOL

### アンステーク優先度上位バリデータ（Top 100）
- 合計減少量: {format_sol(total_unstake)} SOL

## ステーク優先度上位バリデータ一覧
| バリデータ | 優先度 | 変更量(SOL) | marinadeSamTargetSol(E{epoch}) | 入札額(CPMPE) |
|------------|--------|-------------|---------------------|---------------|
"""

    # ステーク優先度でソート
    df_stake_sorted = df_stake.sort_values('stakePriority', ascending=True)
    for _, row in df_stake_sorted.iterrows():
        stake_change = row['stakeChange']
        stake_change_str = f"+{format_sol(stake_change)}" if stake_change > 0 else format_sol(stake_change)
        markdown += f"| {row['voteAccount']} | {int(row['stakePriority'])} | {stake_change_str} | {format_sol(row[f'marinadeStake_{epoch+1}'])} | {format_sol(row['bidCpmpe'])} |\n"

    markdown += f"""
## アンステーク優先度上位バリデータ一覧
| バリデータ | アンステーク優先度 | 変更量(SOL) | marinadeActivatedStakeSol(E{epoch}) | 入札額(CPMPE) | totalPmpe |
|------------|-------------------|-------------|----------------------------------|---------------|-----------|
"""

    # アンステーク変更量でソート
    df_unstake_sorted = df_unstake.sort_values('stakeChange', ascending=True)
    for i, (_, row) in enumerate(df_unstake_sorted.iterrows(), 1):
        stake_change = row['stakeChange']  # アンステークはマイナス値のみ
        markdown += f"| {row['voteAccount']} | {i} | {format_sol(stake_change)} | {format_sol(row[f'marinadeStake_{epoch}'])} | {format_sol(row['bidCpmpe'])} | {format_sol(row['totalPmpe'])} |\n"

    markdown += f"""
## 補足情報
- ステーク分析対象: stakePriorityが1-100のバリデータ
- アンステーク分析対象: ステーク減少量が大きい上位100バリデータ
- データソース: `auctions/{epoch}.*/outputs/results.json`
"""
    
    return markdown

def get_epoch_directory(epoch: int) -> str:
    """エポックのディレクトリパスを取得"""
    auction_dirs = glob(f"auctions/{epoch}.*")
    if not auction_dirs:
        raise ValueError(f"No data directory found for epoch {epoch}")
    return auction_dirs[0]

def fetch_epoch_data(epoch: int) -> Dict:
    """指定されたエポックのデータを取得"""
    try:
        epoch_dir = get_epoch_directory(epoch)
        results_file = os.path.join(epoch_dir, "outputs", "results.json")
        
        if not os.path.exists(results_file):
            raise ValueError(f"Results data not found for epoch {epoch}")
            
        with open(results_file, 'r') as f:
            data = json.load(f)
            
        if not isinstance(data, dict) or 'auctionData' not in data:
            raise ValueError(f"Invalid data format for epoch {epoch}")
            
        return data['auctionData']
    except Exception as e:
        print(f"Error fetching data for epoch {epoch}: {str(e)}")
        sys.exit(1)

def get_top_100_by_stake_priority(data: Dict) -> List[str]:
    """ステークプライオリティが1-100のバリデータを取得"""
    try:
        validators = data['validators']
        filtered_validators = [
            v for v in validators 
            if 1 <= float(v.get('stakePriority', 0)) <= 100
        ]
        sorted_validators = sorted(
            filtered_validators,
            key=lambda x: float(x.get('stakePriority', 0)),
            reverse=False
        )
        return [v['voteAccount'] for v in sorted_validators]
    except (KeyError, ValueError) as e:
        print(f"Error processing validator data: {str(e)}")
        sys.exit(1)

def get_top_100_by_unstake(data_current: Dict, data_next: Dict) -> List[str]:
    """アンステーク量が大きい上位100のバリデータを取得"""
    try:
        all_changes = []
        for validator in data_current['validators']:
            vote_account = validator['voteAccount']
            validator_next = next(
                (v for v in data_next['validators'] if v['voteAccount'] == vote_account),
                None
            )
            if validator_next:
                stake_current = float(validator.get('marinadeActivatedStakeSol', 0))
                stake_next = float(validator_next.get('marinadeActivatedStakeSol', 0))
                stake_change = stake_next - stake_current
                if stake_change < 0:  # アンステークの場合のみ
                    all_changes.append((vote_account, stake_change))
        
        # 変更量の昇順（マイナスが大きい順）で上位100を取得
        all_changes.sort(key=lambda x: x[1])
        return [v[0] for v in all_changes[:100]]
    except (KeyError, ValueError) as e:
        print(f"Error processing unstake data: {str(e)}")
        sys.exit(1)

def create_validator_dataframe(validators: List[str], data_current: Dict, data_next: Dict, epoch: int) -> pd.DataFrame:
    """バリデータのデータフレームを作成"""
    results = []
    for vote_account in validators:
        validator_current = next(
            (v for v in data_current['validators'] if v['voteAccount'] == vote_account),
            None
        )
        validator_next = next(
            (v for v in data_next['validators'] if v['voteAccount'] == vote_account),
            None
        )

        if validator_current and validator_next:
            try:
                stake_current = float(validator_current.get('marinadeActivatedStakeSol', 0))
                stake_next = float(validator_next.get('marinadeActivatedStakeSol', 0))
                stake_change = stake_next - stake_current

                results.append({
                    'voteAccount': vote_account,
                    'stakePriority': float(validator_current.get('stakePriority', 0)),
                    'totalActivatedStakeSol': float(validator_current.get('totalActivatedStakeSol', 0)),
                    'bondBalanceSol': float(validator_current.get('bondBalanceSol', 0)),
                    'bidCpmpe': float(validator_current.get('bidCpmpe', 0)),
                    'totalPmpe': float(validator_current.get('revShare', {}).get('totalPmpe', 0)),
                    f'marinadeStake_{epoch}': stake_current,
                    f'marinadeStake_{epoch+1}': float(validator_current.get('auctionStake', {}).get('marinadeSamTargetSol', 0)),
                    'stakeChange': stake_change,
                    'stakeChangeAbs': abs(stake_change)
                })
            except (ValueError, TypeError) as e:
                print(f"Warning: Error processing data for validator {vote_account}: {str(e)}")
                continue

    if not results:
        raise ValueError("No valid data found for any validators")

    df = pd.DataFrame(results)
    
    columns = [
        'voteAccount',
        'stakePriority',
        'totalActivatedStakeSol',
        'bondBalanceSol',
        'bidCpmpe',
        'totalPmpe',
        f'marinadeStake_{epoch}',
        f'marinadeStake_{epoch+1}',
        'stakeChange',
        'stakeChangeAbs'
    ]
    df = df[columns]

    numeric_columns = ['stakePriority', 'totalActivatedStakeSol', 'bondBalanceSol', 'bidCpmpe',
                      'totalPmpe', f'marinadeStake_{epoch}', f'marinadeStake_{epoch+1}', 
                      'stakeChange', 'stakeChangeAbs']
    df[numeric_columns] = df[numeric_columns].round(3)

    return df

def main():
    if len(sys.argv) != 2:
        print("Usage: python analyze_stake_changes.py <epoch>")
        sys.exit(1)

    try:
        epoch = int(sys.argv[1])
        if epoch < 0:
            raise ValueError("Epoch must be a positive integer")
            
        print(f"Analyzing stake changes for epoch {epoch}...")
        
        # データ取得
        data_current = fetch_epoch_data(epoch)
        data_next = fetch_epoch_data(epoch + 1)
        
        # ステーク優先度上位100の分析
        print("\nProcessing stake priority validators...")
        stake_validators = get_top_100_by_stake_priority(data_current)
        df_stake = create_validator_dataframe(stake_validators, data_current, data_next, epoch)
        
        # アンステーク上位100の分析
        print("\nProcessing unstake priority validators...")
        unstake_validators = get_top_100_by_unstake(data_current, data_next)
        df_unstake = create_validator_dataframe(unstake_validators, data_current, data_next, epoch)
        
        # 分析結果のディレクトリを作成
        analysis_dir = "analysis_results"
        ensure_directory_exists(analysis_dir)
        
        # Markdown形式で結果を保存
        markdown_content = generate_markdown_summary(df_stake, df_unstake, epoch)
        markdown_file = os.path.join(analysis_dir, f"top_priority_epoch_{epoch}.md")
        with open(markdown_file, "w") as f:
            f.write(markdown_content)
        
        print(f"\nAnalysis results saved to: {markdown_file}")

    except ValueError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 