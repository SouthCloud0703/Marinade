# DS SAM pipeline

Solanaバリデータのオークション結果を分析するためのパイプライン

## セットアップ手順

1. Python仮想環境の作成とアクティベート
```bash
python -m venv .venv
source .venv/bin/activate
```

2. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

## データ更新方法

最新のオークションデータを取得して分析を実行するには：
```bash
./scripts/update_analysis.sh
```

このスクリプトの動作：
- リモートリポジトリの`auctions/`ディレクトリの変更を確認
- 新しいデータがある場合のみ更新を実行
- 分析スクリプトを実行し、CSVファイルを更新

## 分析結果

分析結果は以下のファイルに出力されます：
- `analysis_results/epoch_755_to_latest_analysis.csv`

このファイルには以下の情報が含まれます：
- Epoch 755以降の全バリデータの詳細データ
- 各エポックのバリデータ統計情報
- 以下の主要指標：
  - バリデータの基本情報（vote_account, client_version等）
  - ステーク量（total_activated_stake_sol, marinade_activated_stake_sol）
  - コミッション設定（inflation_commission, mev_commission）
  - 入札情報（bid_pmpe, auction_effective_bid_pmpe）
  - 適格性フラグ（sam_eligible, mnde_eligible）
  - 優先度スコア（stake_priority, unstake_priority）

## オークション実行の再現方法

1. `auctions/{epoch}.{slot}/inputs`ディレクトリから必要なファイルを取得
2. 分析スクリプトを実行して結果を確認

## バリデータトレンド分析

大規模バリデータ（marinade_activated_stake_sol >= 100,000 SOL）の動向を分析するには：
```bash
python scripts/analyze_validators_trend.py
```

このスクリプトは以下の分析を行います：
- marinade_activated_stake_solが100,000 SOL以上のバリデータを抽出
- 以下の指標の分布を計算：
  - bid_pmpe
  - bond_balance_sol
  - stake_priority
  - unstake_priority
- marinade_activated_stake_sol上位10バリデータの詳細分析
  - 各バリデータの全指標を1つの表にまとめて表示
  - 直近10エポックの推移を表示（bid_pmpeが0の場合はスキップ）

分析結果は以下のファイルに出力されます：
- `analysis_results/latest_over200.csv`: 生データ
- `analysis_results/latest_over200_analysis.md`: マークダウン形式のレポート

## バリデータ詳細分析

特定のバリデータの詳細な指標推移を分析するには：
```bash
python scripts/analyze_validator_detail.py <vote_account>
```

このスクリプトは以下の分析を行います：
- 指定されたバリデータの以下の指標を表示：
  - marinade_activated_stake_sol
  - marinade_sam_target_sol
  - bond_balance_sol
  - bid_pmpe
  - stake_priority
- 全エポックのデータを時系列で表示

分析結果は以下のファイルに出力されます：
- `analysis_results/validator_detail_<vote_account_last_8chars>.md`

## Stake Priority分析

Stake Priorityの上位バリデータを分析するには：
```bash
python scripts/analyze_top_priority.py <epoch>
```

このスクリプトは以下の分析を行います：
- 指定エポックのStake Priority 1-30位のバリデータを抽出
- 各バリデータの以下の指標を表示：
  - marinade_activated_stake_sol
  - marinade_sam_target_sol
  - bond_balance_sol
  - bid_pmpe
  - stake_priority
  - 次エポックでのステーク増加量
- サマリー情報として以下を表示：
  - 対象バリデータの合計ステーク量
  - 平均stake_priority
  - 平均bid_pmpe

分析結果は以下のファイルに出力されます：
- `analysis_results/top_priority_epoch_<epoch>.md`