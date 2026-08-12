from fastapi import APIRouter,Depends,status
from app.DB.dependencies import get_auth_service
from app.models.users import LoginRequest,RegisterRequest,TokenResponse
from app.DB.repositories.userrepo import UserRepository
from app.services.AuthService import AuthService
from asyncpg import Connection
router = APIRouter(prefix="/auth",tags=["Authentication"])
@router.post("/login",response_model=TokenResponse)
async def Login(req:LoginRequest,service : AuthService = Depends(get_auth_service)):
    token = await service.login(req)
    return token
@router.post("/signup",status_code=status.HTTP_201_CREATED)
async def Signup(req:RegisterRequest,service : AuthService = Depends(get_auth_service)):
    return await service.register(req)