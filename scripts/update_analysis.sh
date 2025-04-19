#!/bin/bash

# 仮想環境をアクティベート
source .venv/bin/activate

# upstreamの変更をチェック
git fetch upstream main

# auctions/ディレクトリの変更を確認
if git diff --quiet upstream/main HEAD -- auctions/; then
    echo "更新すべきデータがありません。"
    exit 0
fi

# 変更があった場合、upstreamの変更を取得
git pull upstream main