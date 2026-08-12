'''
id serial primary key
email text unique not null
password_hash text not null
created_at timestamp not null default current_timestamp
'''
from pydantic import EmailStr
from asyncpg import Connection
from app.models.users import User
class UserRepository:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def get_user_by_roll(self,roll:str):
        row =  await self.conn.fetchrow("select user_id,roll,password_hash,role from users where roll = $1",roll)
        if row is None:
            return None
        return User(
            id=row["user_id"],
            roll=row["roll"],
            password_hash=row["password_hash"],
            role=row["role"]
        )
    async def create_user(self,roll:str,password:str,role:str):
        id : int = await self.conn.fetchval("insert into users(roll,password_hash,role) values ($1,$2,$3) returning user_id",roll,password,role)
        return id
    async def get_user_by_id(self,id:int)->int:
        return await self.conn.fetchrow("select roll from users where user_id = $1",id)