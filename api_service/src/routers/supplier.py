from typing import List,Optional
from fastapi import APIRouter, Depends, Query
from schemas.models import Supplier, SupplierCreate
from dao.dao import APIDAO
from src.routers.categories import get_admin_user

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

@router.get("/", response_model=List[Supplier])
def get_suppliers(
    category_slug: Optional[str] = Query(None),
    subcategory_slug: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    dao: APIDAO = Depends(APIDAO)
):
    return dao.get_suppliers(category_slug, subcategory_slug, search, city, page, limit)

@router.post("/", response_model=Supplier, dependencies=[Depends(get_admin_user)])
def create_supplier(supplier: SupplierCreate, dao: APIDAO = Depends(APIDAO)):
    return dao.create_supplier(supplier)