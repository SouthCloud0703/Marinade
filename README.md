# Marinade SAM Pipeline データ分析

## 概要
Marinade SAMのバリデータデータを分析するためのパイプライン

## 自動更新の仕組み
1. GitHub Actionsが6時間ごとに実行され、以下の処理を行います：
   - upstreamリポジトリからの更新チェック
   - 新しいデータがある場合は自動的にoriginリポジトリを更新
   - 更新状況をSlackに通知

2. 更新後の作業フロー
   ```bash
   # ローカルリポジトリの更新
   git pull origin main

   # 分析の実行
   python analyze_stake_changes.py <エポック番号>
   ```

## 分析結果
- 分析結果は `analysis_results/` ディレクトリに保存されます
- ファイル名形式: `top_priority_epoch_<エポック番号>.md`

## 通知内容
Slackには以下の3パターンで通知されます：
1. 更新なし：新しいデータがない場合
2. 更新あり：新しいデータを検出した場合
3. エラー：実行中にエラーが発生した場合

## セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

2. 依存関係のインストール
```bash
python -m pip install -r requirements.txt
```

3. upstreamの設定
```bash
git remote add upstream https://github.com/marinade-finance/ds-sam-pipeline.git
```

## 実行方法

### GitHub Actionsワークフロー

1. 自動実行
- 6時間ごとに自動的に実行されます
- 新しいデータがある場合のみ分析を実行します

2. 手動実行
- GitHubリポジトリの「Actions」タブを開く
- 「自動分析ワークフロー」を選択
- 「Run workflow」ボタンをクリック
- 「Run workflow」を再度クリックして実行

### ローカルでの実行

1. データの更新
```bash
bash scripts/update_analysis.sh
```
- upstreamからデータを取得します
- 新しいデータがある場合のみ更新します

2. 分析の実行
```bash
python analyze_stake_changes.py <epoch>
```
- `<epoch>`: 分析対象のエポック番号
- 例: `python analyze_stake_changes.py 772`

## 出力ファイル

分析結果は以下の形式で保存されます：
- パス: `analysis_results/top_priority_epoch_<epoch>.md`
- 内容:
  - ステーク優先度上位バリデータ（Priority 1-100）の分析
  - アンステーク優先度上位バリデータ（Top 100）の分析
  - 全体サマリー（増加量・減少量）

## Slack通知

GitHub Actionsワークフロー実行時に以下の通知が送信されます：
- 分析完了時: 分析結果へのリンクを含む成功通知
- 更新なし時: データ更新なしの通知
- エラー発生時: エラー詳細へのリンクを含む失敗通知