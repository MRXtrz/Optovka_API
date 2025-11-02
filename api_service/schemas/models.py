from pydantic import BaseModel
from typing import Optional,Dict

class LoginData(BaseModel):
    email: str
    password: str

class RegisterData(BaseModel):
    email:str
    passwo:str
    role:str

class Token(BaseModel):
    token:str

class UserPayload(BaseModel):
    id:int
    role:str

class Category(BaseModel):
    id: int
    name: str
    slug: str

class CategoryCreate(BaseModel):
    name: str
    slug: str

class Subcategory(BaseModel):
    id: int
    name:str
    slug:str
    category_id:int

class Supplier(BaseModel):
    name: str
    description:Optional[str]
    image_url:Optional[str]
    category_id: int
    contacts: Dict[str,str]
    hash:str
    category_id: Optional[int] = None 
    subcategory_id: Optional[int] = None

class SupplierCreate(BaseModel):
    name: str
    description: Optional[str]
    image_url: Optional[str]
    category_id: int
    subcategory_id: Optional[int]
    contacts: Dict[str, str]
    
class Product(BaseModel):
    name:str
    supplier_id:int
    is_new:bool=True
    image_url:Optional[str]   
    
class Contacts(BaseModel):
    city: Optional[str] = None
    phone: Optional[str] = None
    url: Optional[str] = None


class SubcategoryCreate(BaseModel):
    name: str
    slug: str
    category_id: int
