from pwdlib import PasswordHash
from authlib.jose import JsonWebToken
from authlib.jose import JoseError
from fastapi import status,HTTPException
from app.settings import Settings
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from app.models.users import CurrentUser
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
setting = Settings()
hasher = PasswordHash.recommended()
jwt = JsonWebToken([setting.alg])
def hash_password(password:str):
    return hasher.hash(password)
def verify_password(password:str,hashed_pass:str):
    if not hasher.verify(password,hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Username or Password."
        )
def create_access_token(user_id:int,role:str)->str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=setting.etime)
    header = {
        "alg":setting.alg
    }
    payload = {
    "sub": str(user_id),
    "role":role,
    "exp": expire
    }
    token = jwt.encode(header,payload,setting.skey)
    return token
def decode_access_token(token:str):
    try:
        claims = jwt.decode(token,setting.skey)
        claims.validate()
        return claims
    except JoseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or Expired Token"
        )
async def get_current_user(token: str = Depends(oauth2_scheme))->CurrentUser:
    claims = decode_access_token(token)
    return CurrentUser(
        id= int(claims["sub"]),
        role = claims["role"]
    )