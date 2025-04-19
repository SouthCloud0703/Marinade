import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz

def calculate_expected_stake(bond, bid, commission, mnde_commission):
    """
    予想される総ステーク量を計算する関数
    
    Parameters:
    -----------
    bond : float
        ボンド残高（SOL）
    bid : float
        入札額（SOL）
    commission : float
        バリデータの手数料率（%）
    mnde_commission : float
        MNDEの手数料率（%）
    
    Returns:
    --------
    float
        予想される総ステーク量（SOL）
    """
    # 基本となるステーク量（ボンドの10倍を想定）
    base_stake = bond * 10
    
    # 手数料による調整係数（手数料が低いほど多くのステークを集められる）
    commission_factor = 1 - (commission / 100)
    mnde_commission_factor = 1 - (mnde_commission / 100)
    
    # 入札額による調整係数（入札額が高いほど多くのステークを集められる）
    bid_factor = 1 + (bid / 100)
    
    # 最終的な予想ステーク量を計算
    expected_stake = base_stake * commission_factor * mnde_commission_factor * bid_factor
    
    return expected_stake

def read_dashboard_data(file_path):
    # スペース区切りのファイルを読み込む（raw stringを使用）
    df = pd.read_csv(file_path, sep=r'\s+', header=None)
    
    # カラム名を設定
    df.columns = [
        'Index',
        'Vote Account',
        'Commission',
        'MNDE Commission',
        'Bid',
        'Bond',
        'APY',
        'Stake',
        'SAM Stake',
        'Marinade Active Stake'
    ]
    
    # 数値型への変換処理
    df['Commission'] = df['Commission'].str.rstrip('%').astype(float)
    df['MNDE Commission'] = df['MNDE Commission'].replace('-', '0%').str.rstrip('%').astype(float)
    df['APY'] = df['APY'].replace('∞', '999999').str.rstrip('%').astype(float)
    
    # 数値カラムのカンマを削除して変換
    numeric_columns = ['Bid', 'Bond', 'Stake', 'SAM Stake', 'Marinade Active Stake']
    for col in numeric_columns:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)
    
    # 予想ステーク量を計算
    df['Expected Stake'] = df.apply(
        lambda row: calculate_expected_stake(
            row['Bond'],
            row['Bid'],
            row['Commission'],
            row['MNDE Commission']
        ),
        axis=1
    )
    
    return df

def generate_markdown_summary(df):
    # 日本時間で実行時刻を取得
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    
    # 合計値を計算
    total_bond = df['Bond'].sum()
    total_sam_stake = df['SAM Stake'].sum()
    total_marinade_stake = df['Marinade Active Stake'].sum()
    total_expected_stake = df['Expected Stake'].sum()
    
    # マークダウン形式で結果を生成
    markdown = f"""# SAMステーク分析
実行日時: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}

## サマリー
- 総Bond残高: {total_bond:.2f} SOL
- 総SAMステーク: {total_sam_stake:.2f} SOL
- 総Marinade Active Stake: {total_marinade_stake:.2f} SOL
- 予想される総ステーク: {total_expected_stake:.2f} SOL

## バリデータ詳細
| Vote Account | Bid | Bond (SOL) | SAM Stake (SOL) | Marinade Active Stake (SOL) | Expected Stake (SOL) |
|-------------|-----|------------|----------------|---------------------------|-------------------|"""
    
    # SAMステークでソートしたバリデータ情報を追加
    for _, row in df.sort_values('SAM Stake', ascending=False).iterrows():
        markdown += f"\n| {row['Vote Account']} | {row['Bid']} | {row['Bond']:.2f} | {row['SAM Stake']:.2f} | {row['Marinade Active Stake']:.2f} | {row['Expected Stake']:.2f} |"
    
    return markdown

def main():
    # 入力ファイルと出力ディレクトリのパスを設定
    input_file = Path('dashboard.md')
    output_dir = Path('analysis_results')
    output_dir.mkdir(exist_ok=True)
    
    # データを読み込んで分析
    df = read_dashboard_data(input_file)
    
    # 分析結果をマークダウンファイルに保存
    markdown_summary = generate_markdown_summary(df)
    output_file = output_dir / 'sam_stake_analysis.md'
    output_file.write_text(markdown_summary)

if __name__ == '__main__':
    main() 