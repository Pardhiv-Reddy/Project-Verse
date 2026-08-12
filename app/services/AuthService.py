from app.models.users import LoginRequest,RegisterRequest,User,TokenResponse
from app.DB.repositories.userrepo import UserRepository
from app.DB.repositories.facultyrepo import FacultyRepository
from app.DB.repositories.studentrepo import StudentRepository
from app.auth.security import hash_password,verify_password,create_access_token
from fastapi import HTTPException,status
import logging
logger = logging.getLogger(__name__)
class AuthService:
    def __init__(self,repo:UserRepository,frepo:FacultyRepository,sturepo:StudentRepository):
        self.urepo = repo
        self.frepo = frepo
        self.sturepo = sturepo
    async def register(self,req:RegisterRequest):
        user : User = await self.urepo.get_user_by_roll(req.roll)
        if user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail = "User Already Exisits."
            )
        hashed_pass = hash_password(req.password)
        id = await self.urepo.create_user(req.roll,hashed_pass,req.role)
        if req.role == "Faculty":
            await self.frepo.add_user_id(id,req.roll)
        if req.role == "Student":
            await self.sturepo.add_user_id(id,req.roll)
        logger.info("User Created Successfully.")
        return {"message":f"User {req.roll} Created Successfully."}
    async def login(self,req:LoginRequest):
        user : User = await self.urepo.get_user_by_roll(req.roll)
        if user is not None:
            verify_password(req.password,user.password_hash)
            logger.info("Login Successfull.")
            token = create_access_token(user.id,user.role)
            return TokenResponse(
                access_token=token,
                token_type="Bearer"
            )
        else :
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Email or Password."
            )