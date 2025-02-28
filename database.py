import sqlite3
from datetime import datetime, timedelta
from utils import get_beijing_time

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot_data.db', check_same_thread=False)
        self.create_tables()
        self.migrate_database()  # 添加数据库迁移

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # 先创建users表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            expire_date TEXT,
            session_file TEXT,
            created_at TEXT,
            user_level INTEGER DEFAULT 0
        )
        ''')
        
        # 创建sessions表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            session_file TEXT,
            account_name TEXT,
            account_id INTEGER,
            is_active INTEGER DEFAULT 0,
            created_at TEXT,
            is_locked INTEGER DEFAULT 0,
            locked_by_task_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (locked_by_task_id) REFERENCES scheduled_tasks (id) ON DELETE SET NULL
        )
        ''')

        # 创建scheduled_tasks表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message_text TEXT,
            rounds_per_day INTEGER,
            interval_hours INTEGER,
            start_time TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            session_id INTEGER,
            last_run_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
        ''')
        
        self.conn.commit()

    def migrate_database(self):
        """执行数据库迁移"""
        cursor = self.conn.cursor()
        try:
            # 检查 last_run_date 列是否存在
            cursor.execute("SELECT last_run_date FROM scheduled_tasks LIMIT 1")
        except sqlite3.OperationalError:
            # 如果列不存在，添加它
            cursor.execute("ALTER TABLE scheduled_tasks ADD COLUMN last_run_date TEXT")
            self.conn.commit()
            print("数据库迁移完成：添加 last_run_date 列")
            
        # 检查sessions表中是否有is_locked列
        try:
            cursor.execute("SELECT is_locked FROM sessions LIMIT 1")
        except sqlite3.OperationalError:
            # 如果列不存在，添加它
            cursor.execute("ALTER TABLE sessions ADD COLUMN is_locked INTEGER DEFAULT 0")
            self.conn.commit()
            print("数据库迁移完成：添加 is_locked 列")
            
        # 检查sessions表中是否有locked_by_task_id列
        try:
            cursor.execute("SELECT locked_by_task_id FROM sessions LIMIT 1")
        except sqlite3.OperationalError:
            # 如果列不存在，添加它
            cursor.execute("ALTER TABLE sessions ADD COLUMN locked_by_task_id INTEGER")
            self.conn.commit()
            print("数据库迁移完成：添加 locked_by_task_id 列")

    def add_user(self, user_id, username):
        cursor = self.conn.cursor()
        current_time = get_beijing_time()
        
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, created_at, user_level) VALUES (?, ?, ?, ?)",
            (user_id, username, current_time.strftime("%Y-%m-%d %H:%M:%S"), 0)  # 默认0级(试用用户)
        )
        self.conn.commit()
        
        # 设置5小时试用期（原来是24小时）
        expire_date = (current_time + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "UPDATE users SET expire_date = ? WHERE user_id = ? AND expire_date IS NULL",
            (expire_date, user_id)
        )
        self.conn.commit()

    def set_user_info(self, user_id, days, level):
        current_time = get_beijing_time()
        expire_date = (current_time + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE users SET expire_date = ?, user_level = ? WHERE user_id = ?",
            (expire_date, level, user_id)
        )
        self.conn.commit()

    def get_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()

    def update_session_file(self, user_id, session_file):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE users SET session_file = ? WHERE user_id = ?",
            (session_file, user_id)
        )
        self.conn.commit()

    def get_all_users(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, username, expire_date FROM users")
        return cursor.fetchall()

    # 添加新的方法来管理定时任务
    def add_scheduled_task(self, user_id, message_text, rounds_per_day, interval_hours, start_time, session_id):
        """添加定时任务，支持指定session"""
        cursor = self.conn.cursor()
        current_time = get_beijing_time()
        
        # 开始一个事务
        try:
            cursor.execute(
                "INSERT INTO scheduled_tasks (user_id, message_text, rounds_per_day, interval_hours, start_time, created_at, session_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (user_id, message_text, rounds_per_day, interval_hours, start_time, current_time.strftime("%Y-%m-%d %H:%M:%S"), session_id)
            )
            task_id = cursor.lastrowid
            
            # 如果指定了session_id，锁定该账号
            if session_id:
                cursor.execute(
                    "UPDATE sessions SET is_locked = 1, locked_by_task_id = ? WHERE id = ?", 
                    (task_id, session_id)
                )
                
            # 提交事务
            self.conn.commit()
            print(f"Added task {task_id} and locked session {session_id}")
            return task_id
            
        except Exception as e:
            # 如果出错，回滚事务
            self.conn.rollback()
            print(f"Error in add_scheduled_task: {e}")
            raise e

    def get_user_tasks(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scheduled_tasks WHERE user_id = ? AND is_active = 1", (user_id,))
        return cursor.fetchall()

    def delete_task(self, task_id, user_id):
        """真正删除定时任务"""
        # 首先解锁该任务锁定的所有账号
        cursor = self.conn.cursor()
        cursor.execute("UPDATE sessions SET is_locked = 0, locked_by_task_id = NULL WHERE locked_by_task_id = ?", (task_id,))
        
        # 然后删除任务
        cursor.execute("DELETE FROM scheduled_tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        self.conn.commit()

    # 添加账号管理相关方法
    def add_session(self, user_id, session_file, account_name, account_id):
        cursor = self.conn.cursor()
        current_time = get_beijing_time()
        cursor.execute(
            "INSERT INTO sessions (user_id, session_file, account_name, account_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, session_file, account_name, account_id, current_time.strftime("%Y-%m-%d %H:%M:%S"))
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_sessions(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE user_id = ?", (user_id,))
        return cursor.fetchall()

    def get_active_session(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE user_id = ? AND is_active = 1", (user_id,))
        return cursor.fetchone()

    def set_session_active(self, session_id, user_id):
        cursor = self.conn.cursor()
        # 先将该用户的所有session设为非活跃
        cursor.execute("UPDATE sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
        # 设置指定session为活跃
        cursor.execute("UPDATE sessions SET is_active = 1 WHERE id = ? AND user_id = ?", (session_id, user_id))
        self.conn.commit()

    def delete_session(self, session_id, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ? AND user_id = ?", (session_id, user_id))
        self.conn.commit()

    def get_session_count(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions WHERE user_id = ?", (user_id,))
        return cursor.fetchone()[0]

    def get_session_by_id(self, session_id):
        """获取指定ID的session信息"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.*, t.message_text, t.rounds_per_day, t.interval_hours, t.start_time, t.last_run_date
            FROM sessions s
            LEFT JOIN scheduled_tasks t ON s.locked_by_task_id = t.id
            WHERE s.id = ?
        """, (session_id,))
        return cursor.fetchone()

    def update_task_last_run(self, task_id, run_date):
        """更新任务的最后执行时间"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE scheduled_tasks SET last_run_date = ? WHERE id = ?",
            (run_date, task_id)
        )
        self.conn.commit()

    def get_task_last_run(self, task_id):
        """获取任务的最后执行时间"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT last_run_date FROM scheduled_tasks WHERE id = ?",
            (task_id,)
        )
        result = cursor.fetchone()
        return result[0] if result else None

    def get_unlocked_sessions(self, user_id):
        """获取用户未被锁定的会话"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE user_id = ? AND is_locked = 0", (user_id,))
        return cursor.fetchall()
    
    def lock_session(self, session_id, task_id):
        """锁定会话，将其分配给特定任务"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE sessions SET is_locked = 1, locked_by_task_id = ? WHERE id = ?", (task_id, session_id))
        self.conn.commit()
    
    def unlock_session(self, session_id):
        """解锁特定会话"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE sessions SET is_locked = 0, locked_by_task_id = NULL WHERE id = ?", (session_id,))
        self.conn.commit()
    
    def unlock_all_sessions_for_task(self, task_id):
        """解锁被特定任务锁定的所有会话"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE sessions SET is_locked = 0, locked_by_task_id = NULL WHERE locked_by_task_id = ?", (task_id,))
        self.conn.commit()
    
    def get_session_lock_info(self, session_id):
        """获取会话的锁定信息"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.is_locked, s.locked_by_task_id, t.start_time 
            FROM sessions s 
            LEFT JOIN scheduled_tasks t ON s.locked_by_task_id = t.id 
            WHERE s.id = ?
        """, (session_id,))
        return cursor.fetchone()

    def get_task_by_id(self, task_id):
        """获取指定ID的任务信息"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scheduled_tasks WHERE id = ?", (task_id,))
        return cursor.fetchone() 