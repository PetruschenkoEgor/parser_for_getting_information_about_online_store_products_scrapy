import requests


def get_sale_percent(price_without_discount, price_with_discount):
    """Получаем скидку на товар в процентах."""

    if price_without_discount is None or price_with_discount is None:
        return 0
    difference = price_without_discount - price_with_discount
    discount_percent = difference / price_without_discount * 100

    return round(discount_percent)


def get_working_proxies():
    """Получение прокси."""

    try:
        response = requests.get("https://proxylist.geonode.com/api/proxy-list?limit=10&page=1&sort_by=lastChecked&sort_type=desc")
        proxies = [f"http://{p['ip']}:{p['port']}" for p in response.json()['data']]
        return proxies
    except:
        return []
