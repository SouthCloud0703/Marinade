#!/bin/bash

# 仮想環境をアクティベート
source .venv/bin/activate

# リモートの変更をチェック
git fetch origin main

# auctions/ディレクトリの変更を確認
if git diff --quiet origin/main HEAD -- auctions/; then
    echo "更新すべきデータがありません。"
    exit 0
fi

# 変更があった場合、リモートの変更を取得
git pull origin main