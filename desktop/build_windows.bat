@echo off
REM بناء نسخة وندوز — الناتج بمجلد dist\Masarat
cd /d "%~dp0"
pip install -r requirements.txt
pyinstaller masarat.spec --noconfirm
echo تم البناء: dist\Masarat
pause
