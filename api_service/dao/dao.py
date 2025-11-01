from typing import Optional
from sqlalchemy import select, insert
from db.config import SessionLocal, Category, Subcategory, Supplier, Product
from schemas.models import CategoryCreate, SubcategoryCreate, SupplierCreate, Product as ProductModel
from exceptions.error import DatabaseError

class APIDAO:
    @staticmethod
    def get_categories():
        with SessionLocal() as db:
            result = db.execute(select(Category)).scalars().all()
            return result

    @staticmethod
    def create_category(category: CategoryCreate):
        with SessionLocal() as db:
            stmt = insert(Category).values(name=category.name, slug=category.slug).on_conflict_do_nothing()
            db.execute(stmt)
            db.commit()
            return db.execute(select(Category).where(Category.slug == category.slug)).scalar_one_or_none()

    @staticmethod
    def get_subcategories(category_id: Optional[int] = None):
        with SessionLocal() as db:
            stmt = select(Subcategory)
            if category_id:
                stmt = stmt.where(Subcategory.category_id == category_id)
            result = db.execute(stmt).scalars().all()
            return result

    @staticmethod
    def create_subcategory(subcategory: SubcategoryCreate):
        with SessionLocal() as db:
            stmt = insert(Subcategory).values(
                name=subcategory.name,
                slug=subcategory.slug,
                category_id=subcategory.category_id
            ).on_conflict_do_nothing()
            db.execute(stmt)
            db.commit()
            return db.execute(select(Subcategory).where(Subcategory.slug == subcategory.slug)).scalar_one_or_none()

    @staticmethod
    def get_suppliers(category_slug: Optional[str] = None, subcategory_slug: Optional[str] = None, search: Optional[str] = None, city: Optional[str] = None, page: int = 1, limit: int = 20):
        with SessionLocal() as db:
            stmt = select(Supplier)
            if category_slug:
                category = db.execute(select(Category.id).where(Category.slug == category_slug)).scalar()
                if category:
                    stmt = stmt.where(Supplier.category_id == category)
            if subcategory_slug:
                subcategory = db.execute(select(Subcategory.id).where(Subcategory.slug == subcategory_slug)).scalar()
                if subcategory:
                    stmt = stmt.where(Supplier.subcategory_id == subcategory)
            if search:
                stmt = stmt.where(Supplier.name.ilike(f"%{search}%"))
            if city:
                stmt = stmt.where(Supplier.contacts['city'].astext.ilike(f"%{city}%")) 
            stmt = stmt.offset((page - 1) * limit).limit(limit)
            result = db.execute(stmt).scalars().all()
            return result

    @staticmethod
    def create_supplier(supplier: SupplierCreate):
        with SessionLocal() as db:
            stmt = insert(Supplier).values(
                name=supplier.name,
                description=supplier.description,
                image_url=supplier.image_url,
                category_id=supplier.category_id,
                subcategory_id=supplier.subcategory_id,
                contacts=supplier.contacts
            )
            db.execute(stmt)
            db.commit()
            return db.execute(select(Supplier).where(Supplier.name == supplier.name)).scalar_one_or_none()

    @staticmethod
    def get_new_products(limit: int = 10):
        with SessionLocal() as db:
            stmt = select(Product).where(Product.is_new == True).limit(limit)
            result = db.execute(stmt).scalars().all()
            return result