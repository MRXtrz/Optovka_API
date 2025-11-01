from typing import List
from fastapi import APIRouter, Depends, HTTPException
from schemas.models import Category, CategoryCreate
from dao.dao import APIDAO
from exceptions.error import ForbiddenError
import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/categories", tags=["categories"])
security = HTTPBearer()

SECRET_KEY = "helloworld"  

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise ForbiddenError("Admin access required").to_http()
    return current_user

@router.get("/", response_model=List[Category])
def get_categories(dao: APIDAO = Depends(APIDAO)):
    return dao.get_categories()

@router.post("/", response_model=Category, dependencies=[Depends(get_admin_user)])
def create_category(category: CategoryCreate, dao: APIDAO = Depends(APIDAO)):
    return dao.create_category(category)