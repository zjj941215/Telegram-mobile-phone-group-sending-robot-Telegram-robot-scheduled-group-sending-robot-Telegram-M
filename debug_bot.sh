#!/bin/bash
cd ~/bot
export TZ=Asia/Shanghai
export DEBUG_MODE=1
date > debug.log
echo "Starting bot in debug mode..." >> debug.log
nohup python3 -u bot.py >> debug.log 2>&1 &
