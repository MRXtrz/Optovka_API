from typing import List
from fastapi import APIRouter, Depends
from schemas.models import Product
from dao.dao import APIDAO

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/new", response_model=List[Product])
def get_new_products(dao: APIDAO = Depends(APIDAO)):
    return dao.get_new_products()