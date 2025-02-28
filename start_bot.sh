#!/bin/bash
cd ~/bot
export TZ=Asia/Shanghai
date > bot.log
echo "Starting bot..." >> bot.log
echo "Python version: $(python3 --version)" >> bot.log
echo "Current timezone: $(date)" >> bot.log
echo "Installed packages:" >> bot.log
pip3 list | grep -E "python-telegram-bot|telethon" >> bot.log
nohup python3 bot.py >> bot.log 2>&1 &
