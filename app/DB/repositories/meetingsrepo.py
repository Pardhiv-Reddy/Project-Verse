'''
id serial primary key
title text not null
description text
meeting_time timestamp without time zone 
venue text
created_at timestamp without time zone defualt now()
team_id text
'''
from asyncpg import Connection
from datetime import datetime
class MeetingsRepo:
    def __init__(self,conn:Connection):
        self.conn = conn
    async def create_meeting(self,title:str,description:str,meeting_time:datetime,venue:str,team_id:str)->int:
        id = await self.conn.fetchval("insert into meetings(title,description,meeting_time,venue,team_id) values ($1,$2,$3,$4,$5) returning id",title,description,meeting_time,venue,team_id)
        return id