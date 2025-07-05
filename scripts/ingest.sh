#!/bin/bash
cd backend/workflows

# 如果 .venv 不存在才建立
if [ ! -d ".venv" ]; then
    echo "[info] Creating virtual environment..."
    python3 -m venv .venv
fi

# 啟動虛擬環境
source .venv/bin/activate

# 安裝依賴（你可以視情況決定要不要每次都跑）
pip install -r requirements.txt

# 執行腳本
python etl_script.py
