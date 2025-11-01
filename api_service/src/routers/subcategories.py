from typing import Optional,List
from fastapi import APIRouter, Depends, Query
from schemas.models import Subcategory, SubcategoryCreate
from dao.dao import APIDAO
from src.routers.categories import get_admin_user

router = APIRouter(prefix="/subcategories", tags=["subcategories"])

@router.get("/", response_model=List[Subcategory])
def get_subcategories(category_id: Optional[int] = Query(None), dao: APIDAO = Depends(APIDAO)):
    return dao.get_subcategories(category_id)

@router.post("/", response_model=Subcategory, dependencies=[Depends(get_admin_user)])
def create_subcategory(subcategory: SubcategoryCreate, dao: APIDAO = Depends(APIDAO)):
    return dao.create_subcategory(subcategory)