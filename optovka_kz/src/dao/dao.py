from sqlalchemy import select, insert
from src.db.db import SessionLocal, Category, Subcategory, Supplier, Product
import logging

logger = logging.getLogger(__name__)

class ParserDAO:
    @staticmethod
    def save_category(category):
        with SessionLocal() as db:
            stmt = insert(Category).values(
                name=category.name,
                slug=category.slug
            )
            try:
                db.execute(stmt)
                db.commit()
            except Exception:
                db.rollback()
            result = db.execute(select(Category).where(Category.slug == category.slug)).scalar_one_or_none()
            return result

    @staticmethod
    def save_supplier(supplier):
        with SessionLocal() as db:
            existing = db.execute(select(Supplier).where(Supplier.name == supplier.name)).first()
            if existing:
                return existing

            stmt = insert(Supplier).values(

            )
            try:
                db.execute(stmt)
                db.commit()
            except Exception:
                db.rollback()

            result = db.execute(select(Supplier).where(Supplier.name == supplier.name)).first()
            return result

    @staticmethod
    def save_product(product):
        with SessionLocal() as db:
            stmt = insert(Product).values(
                name=product.name,
                supplier_id=product.supplier_id,
                is_new=product.is_new,
                image_url=product.image_url,
                price=getattr(product, 'price', None),
                description=getattr(product, 'description', None)
            )
            try:
                db.execute(stmt)
                db.commit()
            except Exception:
                db.rollback()

    @staticmethod
    def get_category_id(slug: str):
        with SessionLocal() as db:
            result = db.execute(select(Category.id).where(Category.slug == slug)).scalar()
            return result

    @staticmethod
    def get_supplier_id(name: str):
        with SessionLocal() as db:
            result = db.execute(select(Supplier.id).where(Supplier.name == name)).scalar()
            return result

    @staticmethod
    def get_category_by_slug(slug: str):
        with SessionLocal() as db:
            return db.execute(select(Category).where(Category.slug == slug)).scalar_one_or_none()

    @staticmethod
    def get_subcategory_by_id(slug: str):
        with SessionLocal() as db:
            return db.execute(select(Subcategory.id).where(Subcategory.slug == slug)).scalar_one_or_none()

    def save_subcategory(self, subcategory):
        with SessionLocal() as session:
            stmt = insert(Subcategory).values(
                name=subcategory.name,
                slug=subcategory.slug,
                category_id=subcategory.category_id
            )
            try:
                session.execute(stmt)
                session.commit()
                return True
            except Exception:
                session.rollback()
                return False
