from datetime import datetime, timezone, timedelta

def get_beijing_time():
    utc_time = datetime.now(timezone.utc)
    beijing_time = utc_time.astimezone(timezone(timedelta(hours=8)))
    return beijing_time

# 用户等级相关常量
LEVEL_NAMES = {
    0: "试用用户",
    1: "VIP用户",
    2: "高级VIP用户"
}

MAX_SESSIONS = {
    0: 1,  # 试用用户：1个账号
    1: 5,  # VIP用户：5个账号
    2: 10  # 高级VIP用户：10个账号
}

def get_level_name(level):
    return LEVEL_NAMES.get(level, "未知等级")

def get_max_sessions(level):
    return MAX_SESSIONS.get(level, 0)

def format_time_remaining(expire_date):
    """格式化剩余时间"""
    if not expire_date:
        return "未设置"
    try:
        expire = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S")
        expire = expire.replace(tzinfo=timezone(timedelta(hours=8)))
        now = get_beijing_time()
        if expire < now:
            return "已过期"
        remaining = expire - now
        days = remaining.days
        hours = remaining.seconds // 3600
        return f"{days}天{hours}小时"
    except Exception:
        return "时间格式错误" 