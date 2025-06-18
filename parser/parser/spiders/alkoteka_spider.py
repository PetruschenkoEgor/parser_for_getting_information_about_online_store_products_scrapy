from datetime import datetime
import json
import urllib

import scrapy

from ..utils import get_sale_percent

START_URLS = [
    "https://alkoteka.com/catalog/krepkiy-alkogol",
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2",
    "https://alkoteka.com/catalog/vino"
]
API_URL = "https://alkoteka.com/web-api/v1/product"


class AlkotekaSpider(scrapy.Spider):
    """Паук для Alkoteka."""

    name = "alkoteka"

    # Список категорий и параметры
    categories = []

    for url in START_URLS:
        slug = url.split("/")[-1]
        params = {
            "city_uuid": "4a70f9e0-46ae-11e7-83ff-00155d026416",
            "page": 1,
            "per_page": 100,
            "root_category_slug": slug,
        }
        categories.append(params)

    def start_requests(self):
        for params in self.categories:
            url = f"{API_URL}?{urllib.parse.urlencode(params)}"
            yield scrapy.Request(url, headers={"Accept": "application/json"}, callback=self.parse_api, meta={'page': 1, 'original_params': params})

    def parse_api(self, response):
        try:
            self.logger.info(f"Используется прокси: {response.meta.get('proxy', 'ПРОКСИ НЕ ИСПОЛЬЗУЕТСЯ')}")
            data = json.loads(response.text)
            current_page = response.meta['page']
            original_params = response.meta['original_params']

            products = data.get("results", [])

            if not products:
                return

            for product in products:
                try:
                    originals = product.get("prev_price")
                    current = product.get("price")
                    sale = get_sale_percent(originals, current)
                    quantity = product.get("quantity_total", 0)
                    filter_labels = product.get("filter_labels", [])

                    # Безопасное формирование title
                    title = product.get("name", "")
                    if filter_labels and len(filter_labels) > 0:
                        title += f", {filter_labels[0].get('title', '')}"

                    item = {
                        "timestamp": datetime.now().isoformat(),
                        "RPC": product.get("vendor_code", ""),
                        "url": product.get("product_url", ""),
                        "title": title,
                        "marketing_tags": product.get("action_labels", []),
                        "brand": "",
                        "section": [
                            product.get("category", {}).get("parent", {}).get("name", ""),
                            product.get("category", {}).get("name", "")
                        ],
                        "price_data": {
                            "current": float(current) if current is not None else 0.0,
                            "original": float(originals) if originals is not None else float(
                                current) if current is not None else 0.0,
                            "sale_tag": f"Скидка {sale}%" if sale > 0 else "Скидки нет",
                        },
                        "stock": {
                            "in_stock": quantity > 0,
                            "count": quantity,
                        },
                        "assets": {
                            "main_image": product.get("image_url", ""),
                            "set_images": [product.get("image_url", "")],
                            "view360": [],
                            "video": []
                        },
                        "metadata": {
                            "__description": product.get("description", ""),
                            "product_key": product.get("vendor_code", ""),
                            "color": filter_labels[3].get("title") if len(filter_labels) > 3 else None,
                            "obem": filter_labels[0].get("title") if filter_labels else None,
                        },
                    }
                    yield item
                except Exception as product_error:
                    print(f"Ошибка обработки товара: {product_error}")

            has_next_page = False

            # Если текущая страница вернула максимальное количество товаров
            if len(products) == original_params["per_page"]:
                has_next_page = True

            # Если есть следующая страница - делаем запрос
            if has_next_page:
                next_page = current_page + 1
                next_params = original_params.copy()
                next_params["page"] = next_page

                yield scrapy.Request(
                    url=f"{API_URL}?{urllib.parse.urlencode(next_params)}",
                    headers={"Accept": "application/json"},
                    callback=self.parse_api,
                    meta={'page': next_page, 'original_params': original_params}
                )
            else:
                self.logger.info(f"Пагинация завершена. Всего страниц: {current_page}")
        except Exception as e:
            print(e)
