#!/usr/bin/env bash
# بناء نسخة لينكس — الناتج بمجلد dist/Masarat
set -e
cd "$(dirname "$0")"
pip install -r requirements.txt --break-system-packages
pyinstaller masarat.spec --noconfirm
echo "تم البناء: dist/Masarat"
