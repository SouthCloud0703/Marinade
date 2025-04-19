#!/bin/bash

# 作業ディレクトリに移動
cd "$(dirname "$0")"

# update_analysisを実行
./update_analysis.sh

# 最新のエポックを取得
latest_epoch=$(ls -d auctions/*/ | grep -o '[0-9]*' | sort -n | tail -n 1)
previous_epoch=$((latest_epoch - 1))

# 分析スクリプトを実行
python3 analyze_stake_changes.py $previous_epoch 