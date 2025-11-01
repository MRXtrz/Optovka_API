from fastapi import APIRouter, HTTPException
from schemas.models import LoginData, Token
import requests

router = APIRouter(prefix="/auth", tags=["auth"])

AUTH_URL = "https://b2b-f014.onrender.com/auth/login" 

@router.post("/login", response_model=Token)
def login(data: LoginData):
    try:
        response = requests.post(AUTH_URL, json=data.dict())
        response.raise_for_status()
        return Token(token=response.json()["token"])  
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=response.status_code if 'response' in locals() else 500, detail=str(e))