import asyncpg
from dotenv import load_dotenv
from app.settings import Settings
load_dotenv()
setting = Settings()
class DataBase:
    def __init__(self):
        self.pool = None
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host = setting.host,
            port = setting.port,
            user = setting.user,
            password = setting.password,
            database = setting.name,
            min_size=5,
            max_size=20,
            max_inactive_connection_lifetime=30
        )
    async def close(self):
        await self.pool.close()
db = DataBase()