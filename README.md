# Marinade SAM Pipeline

このリポジトリは、Marinade SAMのステーク変更分析を行うためのパイプラインです。

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/SouthCloud0703/Marinade.git
cd Marinade
```

2. upstreamリポジトリの設定
```bash
git remote add upstream https://github.com/marinade-finance/ds-sam-pipeline.git
```

3. 仮想環境のセットアップ
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

4. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

## 手動実行手順

### 1. データの更新確認

以下のコマンドを実行して、upstreamリポジトリからデータの更新を確認します：

```bash
source scripts/update_analysis.sh
```

- 終了コード0: 更新なし
- 終了コード1: 更新あり（auctionsディレクトリが更新されます）

### 2. ステーク変更の分析

最新のエポックに対して分析を実行します：

```bash
python analyze_stake_changes.py <epoch_number>
```

- `<epoch_number>`: 分析対象のエポック番号
- 分析結果は `analysis_results/top_priority_epoch_<epoch_number>.md` に保存されます

## 分析結果

分析結果には以下の情報が含まれます：

- 全体サマリー（ステーク増減の合計）
- ステーク優先度の高いバリデーターの変更
- アンステーク優先度の高いバリデーターの変更

## 注意事項

- GitHub Actionsによる自動実行は現在無効化されています
- 分析は手動で実行する必要があります
- upstreamリポジトリからの更新は `auctions` ディレクトリのみを対象としています