import json
import pandas as pd
from pathlib import Path
import glob

def find_auction_directories():
    # epoch 755以降のディレクトリを検索
    pattern = 'auctions/[7-9][0-9][0-9].*'
    matching_dirs = glob.glob(pattern)
    
    # epochの番号でソート
    matching_dirs.sort(key=lambda x: int(x.split('/')[1].split('.')[0]))
    
    # epoch 755以降のディレクトリのみをフィルタリング
    matching_dirs = [d for d in matching_dirs if int(d.split('/')[1].split('.')[0]) >= 755]
    
    if not matching_dirs:
        raise FileNotFoundError(f'対象のepochディレクトリが見つかりません')
    
    return matching_dirs

def analyze_epoch_results(auction_dir):
    json_path = Path(auction_dir) / 'outputs/results.json'
    epoch_number = int(auction_dir.split('/')[1].split('.')[0])
    
    if not json_path.exists():
        print(f'警告: 結果ファイルが見つかりません: {json_path}')
        return None
    
    # JSONファイルを読み込む
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # バリデータ情報を取得
    validators = data['auctionData']['validators']
    
    # 必要な情報を抽出してデータフレームを作成
    validator_data = []
    for validator in validators:
        validator_info = {
            'epoch': epoch_number,
            'vote_account': validator['voteAccount'],
            'client_version': validator['clientVersion'],
            'vote_credits': validator['voteCredits'],
            'aso': validator['aso'],
            'country': validator['country'],
            'bond_balance_sol': validator['bondBalanceSol'],
            'total_activated_stake_sol': validator['totalActivatedStakeSol'],
            'marinade_activated_stake_sol': validator['marinadeActivatedStakeSol'],
            'inflation_commission': validator['inflationCommissionDec'],
            'mev_commission': validator['mevCommissionDec'],
            'bid_cpmpe': validator['bidCpmpe'],
            'mnde_votes_sol_value': validator['mndeVotesSolValue'],
            'mnde_stake_cap_increase': validator['mndeStakeCapIncrease']
        }
        
        # revShare情報を追加
        if 'revShare' in validator:
            validator_info.update({
                'bid_pmpe': validator['revShare'].get('bidPmpe'),
                'auction_effective_bid_pmpe': validator['revShare'].get('auctionEffectiveBidPmpe')
            })
        
        # auctionStake情報を追加
        if 'auctionStake' in validator:
            validator_info.update({
                'external_activated_sol': validator['auctionStake']['externalActivatedSol'],
                'marinade_mnde_target_sol': validator['auctionStake']['marinadeMndeTargetSol'],
                'marinade_sam_target_sol': validator['auctionStake']['marinadeSamTargetSol']
            })
        
        # 適格性情報を追加
        validator_info.update({
            'sam_eligible': validator.get('samEligible', False),
            'mnde_eligible': validator.get('mndeEligible', False),
            'stake_priority': validator.get('stakePriority'),
            'unstake_priority': validator.get('unstakePriority')
        })
        
        # バリデータ情報をリストに追加
        validator_data.append(validator_info)
    
    return pd.DataFrame(validator_data)

def analyze_all_epochs():
    # 全対象ディレクトリを取得
    auction_dirs = find_auction_directories()
    
    # 各epochのデータを格納するリスト
    all_data = []
    
    # 各epochのデータを処理
    for auction_dir in auction_dirs:
        epoch_number = int(auction_dir.split('/')[1].split('.')[0])
        print(f'Epoch {epoch_number} を処理中...')
        
        df = analyze_epoch_results(auction_dir)
        if df is not None:
            all_data.append(df)
    
    # 全データを結合
    if not all_data:
        raise ValueError('処理可能なデータが見つかりませんでした')
    
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # 数値データの列を特定
    numeric_columns = combined_df.select_dtypes(include=['float64', 'int64']).columns
    
    # CSVファイルとして保存
    output_dir = Path('analysis_results')
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f'epoch_755_to_latest_analysis.csv'
    combined_df.to_csv(output_path, index=False)
    
    print(f'\n分析結果を保存しました: {output_path}')
    
    # 数値データの基本統計情報を計算
    stats_df = combined_df[numeric_columns].describe()
    return combined_df, stats_df

if __name__ == '__main__':
    try:
        # 全epochのデータを分析
        df, stats_df = analyze_all_epochs()
        
        # 基本的な統計情報を表示
        print('\n基本統計情報:')
        print(stats_df)
        
        print('\nデータセットの形状:', df.shape)
        print('含まれるepoch:', sorted(df['epoch'].unique()))
        print('列名一覧:', list(df.columns))
    except Exception as e:
        print(f'エラーが発生しました: {str(e)}') 