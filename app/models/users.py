from pydantic import BaseModel,EmailStr
from datetime import datetime
class RegisterRequest(BaseModel):
    roll: str
    password: str
    role : str

class LoginRequest(BaseModel):
    roll: str
    password: str
    role : str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id : int
    roll : str
    password_hash : str
    role : str

class CurrentUser(BaseModel):
    id : int
    role : str