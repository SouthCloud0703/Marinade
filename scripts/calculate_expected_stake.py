import pandas as pd
from pathlib import Path
import argparse

def calculate_expected_stake(bond, bid):
    """
    予想される総ステーク量を計算する関数
    
    Parameters:
    -----------
    bond : float
        ボンド残高（SOL）
    bid : float
        入札額（CPMPE）
    
    Returns:
    --------
    float
        予想される総ステーク量（SOL）
    """
    # PMPEの計算
    bid_pmpe = bid / 1000  # CPMPEをPMPEに変換
    
    # ステークキャップの計算
    # stakeCap = bondBalanceSol / (refundableDepositPerStake + downtimeProtectionPerStake + bidPerStake)
    downtime_protection_per_stake = 0  # 現在は0に設定
    refundable_deposit_per_stake = bid_pmpe  # PMPEをそのままper stakeとして使用
    bid_per_stake = bid_pmpe  # PMPEをそのままper stakeとして使用
    
    stake_cap = bond / (refundable_deposit_per_stake + downtime_protection_per_stake + bid_per_stake)
    
    return stake_cap

def main():
    parser = argparse.ArgumentParser(description='バリデータの予想ステーク量を計算')
    parser.add_argument('--bond', type=float, required=True, help='ボンド残高（SOL）')
    parser.add_argument('--bid', type=float, required=True, help='入札額（CPMPE）')
    
    args = parser.parse_args()
    
    expected_stake = calculate_expected_stake(
        args.bond,
        args.bid
    )
    
    # PMPEの計算
    bid_pmpe = args.bid / 1000
    
    print(f"""
予想ステーク量の計算結果:
------------------------
ボンド残高: {args.bond:.2f} SOL
入札額: {args.bid:.4f} CPMPE
------------------------
予想される総ステーク量: {expected_stake:.2f} SOL

計算内訳:
- 入札PMPE: {bid_pmpe:.6f}
- refundableDepositPerStake: {bid_pmpe:.9f}
- bidPerStake: {bid_pmpe:.9f}
- 合計係数: {(bid_pmpe + bid_pmpe):.9f}
""")

if __name__ == '__main__':
    main() 