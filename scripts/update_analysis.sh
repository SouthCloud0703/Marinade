#!/bin/bash

# 仮想環境をアクティベート
source .venv/bin/activate

# upstreamから最新の変更を取得
git fetch upstream main

# auctionsディレクトリに更新があるか確認
if git diff --quiet upstream/main HEAD -- auctions/; then
    echo "No updates found in auctions directory"
    exit 0
fi

# auctionsディレクトリのみを更新
git checkout upstream/main -- auctions/

# 更新があったことを示すために終了コード1を返す
exit 1