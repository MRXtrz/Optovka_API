import hashlib
import logging
from urllib.parse import urljoin
from src.schemas import models as schemas_models
from src.dao.dao import ParserDAO
from src.db import db as db_module

logger = logging.getLogger(__name__)

class ScrapingError(Exception):
    pass

class ParserService:
    def __init__(self):
        self.dao = ParserDAO()

    def _safe_text(self, response, selector: str, default: str = "") -> str:
        try:
            val = response.css(selector).get(default=default)
            return val.strip() if isinstance(val, str) else default
        except Exception:
            return default

    def _safe_attr(self, response, selector: str, default: str = "") -> str:
        try:
            val = response.css(selector).get(default=default)
            return val or default
        except Exception:
            return default

    def parse_category(self, response, url: str, name: str) -> str:
        try:
            slug = url.rstrip('/').split('/')[-1] if url else None
            if not slug:
                raise ScrapingError("Cannot determine category slug from URL")

            class C: pass
            c = C()
            c.name = name
            c.slug = slug

            saved = self.dao.save_category(c)
            return slug
        except Exception as e:
            logger.exception("Failed to parse category")
            raise

    def parse_subcategory(self, name: str, slug: str, category_slug: str) -> bool:
        try:
            category = self.dao.get_category_by_slug(category_slug)
            if not category:
                logger.error(f"Category '{category_slug}' not found")
                return False

            class S: pass
            s = S()
            s.name = name
            s.slug = slug
            s.category_id = category.id

            saved = self.dao.save_subcategory(s)
            logger.info(f"Saved subcategory: {name} (slug: {slug})")
            return saved
        except Exception as e:
            logger.exception(f"Failed subcategory {name}: {e}")
            return False

    def parse_supplier(self, response, name, url, city, phone, category_slug, description=None, image_url=None, subcategory_slug=None) -> None:
        try:
            logger.info(f"Parsing supplier: {name} | City: {city} | Category: {category_slug} | Phone: {phone} | URL: {url}")
            category = self.dao.get_category_by_slug(category_slug)
            if not category:
                raise ScrapingError(f"Category with slug '{category_slug}' not found")

            subcategory_id = None
            if subcategory_slug:
                subcat = self.dao.get_category_by_slug(subcategory_slug)
                if subcat:
                    subcategory_id = subcat.id

            unique_string = f"{name}-{url}-{city}-{phone}"
            supplier_hash = hashlib.md5(unique_string.encode('utf-8')).hexdigest()

            contacts = {"city": city or "", "phone": phone or "", "url": url or ""}

            class Sup: pass
            sup = Sup()
            sup.name = name
            sup.description = description
            sup.image_url = image_url
            sup.category_id = category.id
            sup.contacts = contacts
            sup.subcategory_id = subcategory_id
            sup.hash = supplier_hash

            self.dao.save_supplier(sup)
            logger.info(f"Saved supplier: {name} ({city})")
        except Exception as e:
            logger.exception("Failed to parse supplier")
            raise

    def parse_product(self, response, supplier_name: str) -> None:
        try:
            name = (
                response.css('span[itemprop="name"]::text').get()
                or response.css('.c-c-name span[itemprop="name"]::text').get()
                or response.css('.c-c-name span::text').get()
                or response.css('h3::text').get()
                or response.css('.product-name::text').get()
            )
            
            if not name:
                name = "unknown-product"
            
            name = name.strip()

            supplier_id = self.dao.get_supplier_id(supplier_name)
            if supplier_id is None:
                logger.warning("Supplier '%s' not found when parsing product '%s'", supplier_name, name)
                return

            image_src = (
                response.css('img[itemprop="image"]::attr(src)').get()
                or response.css('.f-g-foto-block img::attr(src)').get()
                or response.css('.f-g-foto img::attr(src)').get()
                or response.css('img::attr(src)').get()
                or ''
            )
            image_url = urljoin(response.url, image_src) if image_src else ''

            price = None
            offers_span = response.css('span[itemprop="offers"]')
            if offers_span:
                price = offers_span.css('meta[itemprop="price"]::attr(content)').get()
                if not price:
                    price_text = offers_span.css('::text').get()
                    if price_text and 'тенге' in price_text:
                        price = price_text.strip()
            
            if not price:
                price = response.css('meta[itemprop="price"]::attr(content)').get()
            
            if price:
                price = price.strip()
            
            description = response.css('meta[itemprop="description"]::attr(content)').get()
            if not description:
                about_div = response.css('.c-c-about')
                if about_div:
                    description_parts = about_div.css('::text').getall()
                    if description_parts:
                        description = " ".join([d.strip() for d in description_parts if d.strip()])
                        description = description.strip() if description else None
            
            if not description:
                description = None

            logger.info(f"Parsing product: name='{name}', price='{price}', description_length={len(description) if description else 0}")

            class P: pass
            p = P()
            p.name = name
            p.supplier_id = supplier_id
            p.is_new = True
            p.image_url = image_url
            p.price = price if price else None
            p.description = description

            self.dao.save_product(p)
            logger.info(f"Saved product: {name} (price: {price}) for supplier {supplier_name}")
        except Exception as e:
            logger.exception(f"Failed to parse product. URL: {getattr(response, 'url', 'unknown')}")
            raise

    def parse_product_from_listing(self, name: str, supplier_name: str, image_url: str = None) -> None:
        try:
            if not name:
                logger.warning("Product name is empty, skipping")
                return
                
            name = name.strip()
            
            supplier_id = self.dao.get_supplier_id(supplier_name)
            if supplier_id is None:
                logger.warning("Supplier '%s' not found when parsing product '%s'", supplier_name, name)
                return

            class P: pass
            p = P()
            p.name = name
            p.supplier_id = supplier_id
            p.is_new = True
            p.image_url = image_url or ''

            self.dao.save_product(p)
            logger.info(f"Saved product from listing: {name} for supplier {supplier_name}")
        except Exception as e:
            logger.exception(f"Failed to parse product from listing: {e}")
            raise
