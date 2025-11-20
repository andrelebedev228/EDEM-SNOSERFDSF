import aiosqlite
import datetime

DATABASE = 'database.db'

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                subscription_active BOOLEAN DEFAULT FALSE,
                subscription_expires_at TIMESTAMP
            )
        ''')
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT * FROM users WHERE id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row

async def add_user(user_id: int, username: str, subscription_active: bool, subscription_expires_at: datetime.datetime = None):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            INSERT INTO users (id, username, subscription_active, subscription_expires_at)
            VALUES (?, ?, ?, ?)
        ''', (user_id, username, subscription_active, subscription_expires_at))
        await db.commit()

async def update_subscription(user_id: int, subscription_active: bool, subscription_expires_at: datetime.datetime):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            UPDATE users
            SET subscription_active = ?, subscription_expires_at = ?
            WHERE id = ?
        ''', (subscription_active, subscription_expires_at, user_id))
        await db.commit()

async def check_subscription(user_id: int):
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT subscription_active, subscription_expires_at FROM users WHERE id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return False

            subscription_active, subscription_expires_at = row

            if subscription_expires_at is not None:
                subscription_expires_at = datetime.datetime.strptime(subscription_expires_at, '%Y-%m-%d %H:%M:%S.%f')

            if subscription_active and (subscription_expires_at is None or subscription_expires_at > datetime.datetime.now()):
                return True

            return False
async def get_oll_users():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            row = await cursor.fetchone()
            return row[0]

async def get_subscrissbed_users():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT COUNT(*) FROM users WHERE subscription_active = 1') as cursor:
            row = await cursor.fetchone()
            return row[0]


async def azimoff_test():
    async with aiosqlite.connect(DATABASE) as db:
        async with db.execute('SELECT id FROM users') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]