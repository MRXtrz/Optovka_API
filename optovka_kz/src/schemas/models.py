from pydantic import BaseModel
from typing import Optional,Dict



class Category(BaseModel):
    name: str
    slug: str
    
# class SubCategory(BaseModel):
#     name:str
#     slug:str

class Supplier(BaseModel):
    name: str
    description:Optional[str]
    image_url:Optional[str]
    category_id: int
    contacts: Dict[str,str]
    hash:Optional[str] 
    
    
class Product(BaseModel):
    name:str
    supplier_id:int
    is_new:bool=True
    image_url:Optional[str]   
    