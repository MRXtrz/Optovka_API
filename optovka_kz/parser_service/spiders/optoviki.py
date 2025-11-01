import logging
from urllib.parse import urljoin

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from src.services.parser_service import ParserService

logger = logging.getLogger(__name__)

class OptovikiSpider(scrapy.Spider):
    name = "optoviki"
    allowed_domains = ["www.optoviki.kz"]
    start_urls = ["https://www.optoviki.kz"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser_service = ParserService()

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.parse_categories,
                wait_time=15,
                wait_until=EC.presence_of_element_located((By.TAG_NAME, "body")),
                dont_filter=True
            )

    def parse_categories(self, response):
        category_links = response.css('a[href*="optom-"]')

        if not category_links:
            logger.warning("No categories found on main page")
            with open('debug_main_page.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return

        seen = set()

        for link in category_links:
            href = link.css('::attr(href)').get()
            name = link.css('::text').get()
            if not href or not name or href in seen:
                continue
            seen.add(href)
            url = urljoin(response.url, href)
            name = name.strip()

            try:
                category_slug = self.parser_service.parse_category(response, url, name)
                logger.info(f"{name} — {url}")
            except Exception as e:
                logger.error(f"Ошибка при сохранении категории {name}: {e}")
                continue

            yield SeleniumRequest(
                url=url,
                callback=self.parse_subcategories,
                meta={'category_name': name, 'category_slug': category_slug},
                wait_time=10,
                dont_filter=True
            )

    def parse_subcategories(self, response):
        category_name = response.meta.get('category_name')
        category_slug = response.meta.get('category_slug')
        subcategory_links = response.css('a[href*="-"]')
        if subcategory_links:
            logger.info(f"Found {len(subcategory_links)} subcategories in {category_name}")
            seen = set()
            for link in subcategory_links:
                href = link.css('::attr(href)').get()
                name = link.css('::text').get()
                if not href or not name or href in seen:
                    continue
                seen.add(href)
                url = urljoin(response.url, href)
                name = name.strip()
                slug = url.rstrip('/').split('/')[-1]

                try:
                    saved = self.parser_service.parse_subcategory(name=name, slug=slug, category_slug=category_slug)
                    subcategory_slug = slug if saved else None
                except Exception as e:
                    logger.error(f"Failed subcategory {name}: {e}")
                    subcategory_slug = None
                    continue

                yield SeleniumRequest(
                    url=url,
                    callback=self.parse_suppliers,
                    meta={
                        'category_name': category_name,
                        'category_slug': category_slug,
                        'subcategory_name': name,
                        'subcategory_slug': subcategory_slug
                    },
                    wait_time=8,
                    dont_filter=True
                )
        else:
            logger.info(f"No subcategories in {category_name}, parsing suppliers directly")
            yield SeleniumRequest(
                url=response.url,
                callback=self.parse_suppliers,
                meta={
                    'category_name': category_name,
                    'category_slug': category_slug,
                    'subcategory_slug': None
                },
                wait_time=8,
                dont_filter=True
            )

    def parse_suppliers(self, response):
        category_name = response.meta.get('category_name')
        category_slug = response.meta.get('category_slug')
        subcategory_slug = response.meta.get('subcategory_slug')

        supplier_items = response.css('li.c-container')

        if not supplier_items:
            logger.warning(f"No suppliers found in {category_name} {'/ ' + subcategory_slug if subcategory_slug else ''}")
            with open(f'debug_suppliers_{category_slug}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            return

        for item in supplier_items:
            name = (item.css('.c-c-name a span::text').get()
                    or item.css('.c-c-name a::text').get()
                    or item.css('.c-c-name span::text').get())
            name = name.strip() if isinstance(name, str) else None

            href = item.css('.c-c-name a::attr(href)').get()
            if href:
                href = urljoin(response.url, href)

            city = item.css('.c-c-region span a::text').get() or None
            if city:
                city = city.strip()

            phone = item.css('.fc-str-right span::text').getall()
            if phone:
                phone = ' '.join([p.strip() for p in phone if p.strip()])
            else:
                phone = None

            logger.info(f"[SUPPLIER] name={name} city={city} phone={phone} subcategory={subcategory_slug}")

            if href:
                yield SeleniumRequest(
                    url=href,
                    callback=self.parse_supplier_detail,
                    meta={
                        'category_slug': category_slug,
                        'subcategory_slug': subcategory_slug,
                        'list_name': name,
                        'list_city': city,
                        'list_phone': phone,
                        'company_url': href
                    },
                    wait_time=8,
                    dont_filter=True
                )
            else:
                try:
                    self.parser_service.parse_supplier(
                        response=response,
                        name=name or "unknown",
                        url=None,
                        city=city,
                        phone=phone,
                        category_slug=category_slug,
                        subcategory_slug=subcategory_slug
                    )
                except Exception as e:
                    logger.error(f"Failed to save supplier (no href) {name}: {e}")

    def parse_supplier_detail(self, response):
        meta = response.meta or {}
        category_slug = meta.get('category_slug')
        subcategory_slug = meta.get('subcategory_slug')
        list_name = meta.get('list_name')
        list_city = meta.get('list_city')
        list_phone = meta.get('list_phone')
        company_url = meta.get('company_url') or response.url
        name = (response.css('h1.firm-head-name::text').get()
                or response.css('.firm-head-name::text').get()
                or list_name)
        name = name.strip() if isinstance(name, str) else None

        city = (response.css('.firm-head-adress::text').get()
                or list_city)
        city = city.strip() if isinstance(city, str) else None

        phone = (
            response.css('a[href^="tel:"]::attr(href)').re_first(r'tel:(.+)')
            or " ".join([p.strip() for p in response.css('.fc-str-right span::text').getall() if p.strip()])
            or response.css('.c-c-phone::text').get()
            or list_phone
        )

        phone = phone.strip() if isinstance(phone, str) else None

        desc_parts = response.css('.firm-content-block *::text, .firm-about *::text').getall()
        description = " ".join([d.strip() for d in desc_parts if d.strip()]) or None

        image_src = response.css('.firm-logo img::attr(src)').get()
        image_url = urljoin(response.url, image_src) if image_src else None

        try:
            self.parser_service.parse_supplier(
                response=response,
                name=name or "unknown",
                url=company_url,
                city=city,
                phone=phone,
                category_slug=category_slug,
                description=description,
                image_url=image_url,
                subcategory_slug=subcategory_slug
            )
            
            supplier_name = name or "unknown"
            self.parse_products_from_supplier_page(response, supplier_name)
            
            all_goods_link = response.css('a[href*="/goods"]::attr(href)').get()
            if all_goods_link:
                import re
                supplier_id_match = re.search(r'/(\d+)', company_url)
                if supplier_id_match:
                    supplier_id = supplier_id_match.group(1)
                    goods_url = urljoin(response.url, f'/{supplier_id}/goods')
                    logger.info(f"Found goods link for {supplier_name}: {goods_url}")
                    yield SeleniumRequest(
                        url=goods_url,
                        callback=self.parse_products_list,
                        meta={'supplier_name': supplier_name},
                        wait_time=10,
                        dont_filter=True
                    )
            
        except Exception as e:
            logger.exception(f"Failed to save supplier detail {company_url}: {e}")

    def parse_products_from_supplier_page(self, response, supplier_name):
        products = response.css('ul.firm-goods-list li[itemscope][itemtype*="Product"]')
        
        for product in products:
            product_name = product.css('span[itemprop="name"]::text').get()
            if not product_name:
                product_name = product.css('.f-g-name span::text').get() or product.css('.f-g-name a::text').get()
            
            if product_name:
                product_name = product_name.strip()
                
                product_link = product.css('a[href*="/goods/"]::attr(href)').get()
                
                image_src = product.css('img[itemprop="image"]::attr(src)').get()
                if not image_src:
                    image_src = product.css('img::attr(src)').get()
                
                image_url = urljoin(response.url, image_src) if image_src else None
                
                if product_link:
                    product_url = urljoin(response.url, product_link)
                    logger.info(f"Found product link: {product_name} -> {product_url}")
                    yield SeleniumRequest(
                        url=product_url,
                        callback=self.parse_product_detail,
                        meta={'supplier_name': supplier_name},
                        wait_time=5,
                        dont_filter=True
                    )
                else:
                    try:
                        self.parser_service.parse_product_from_listing(
                            name=product_name,
                            supplier_name=supplier_name,
                            image_url=image_url
                        )
                        logger.info(f"Parsed product from listing: {product_name}")
                    except Exception as e:
                        logger.error(f"Failed to parse product {product_name}: {e}")

    def parse_products_list(self, response):
        supplier_name = response.meta.get('supplier_name', 'unknown')
        logger.info(f"Parsing products list page: {response.url} for supplier {supplier_name}")
        
        product_links = response.css('a[href*="/goods/"]::attr(href)').getall()
        
        goods_menu_links = response.css('#goods-menu a[href*="/goods/"]::attr(href)').getall()
        
        seen_links = set()
        
        for link in product_links + goods_menu_links:
            if link and link not in seen_links and '/goods/' in link:
                seen_links.add(link)
                product_url = urljoin(response.url, link)
                logger.info(f"Found product URL: {product_url}")
                yield SeleniumRequest(
                    url=product_url,
                    callback=self.parse_product_detail,
                    meta={'supplier_name': supplier_name},
                    wait_time=5,
                    dont_filter=True
                )
        
        products = response.css('li[itemscope][itemtype*="Product"], .c-c-main[itemscope][itemtype*="Product"]')
        for product in products:
            product_name = product.css('span[itemprop="name"]::text').get()
            if product_name:
                product_name = product_name.strip()
                image_src = product.css('img[itemprop="image"]::attr(src)').get() or product.css('img::attr(src)').get()
                image_url = urljoin(response.url, image_src) if image_src else None
                
                try:
                    self.parser_service.parse_product_from_listing(
                        name=product_name,
                        supplier_name=supplier_name,
                        image_url=image_url
                    )
                    logger.info(f"Parsed product from listing page: {product_name}")
                except Exception as e:
                    logger.error(f"Failed to parse product {product_name}: {e}")

    def parse_product_detail(self, response):
        supplier_name = response.meta.get('supplier_name', 'unknown')
        
        product_name = (
            response.css('span[itemprop="name"]::text').get()
            or response.css('.c-c-name span::text').get()
            or response.css('h3::text').get()
            or response.css('.product-name::text').get()
        )
        
        if product_name:
            product_name = product_name.strip()
        else:
            logger.warning(f"Could not find product name on {response.url}")
            return
        
        image_src = (
            response.css('img[itemprop="image"]::attr(src)').get()
            or response.css('.f-g-foto img::attr(src)').get()
            or response.css('img::attr(src)').get()
        )
        image_url = urljoin(response.url, image_src) if image_src else None
        
        try:
            self.parser_service.parse_product(response, supplier_name)
            logger.info(f"Successfully parsed product detail: {product_name} from {response.url}")
        except Exception as e:
            logger.error(f"Failed to parse product detail {response.url}: {e}")
