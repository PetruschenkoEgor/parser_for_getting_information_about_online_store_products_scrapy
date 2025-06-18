## Проект - parser_for_getting_information_about_online_store_products_scrapy

## Описание
Это программа для парсинга данных с онлайн магазина алкотека.

## Установка
1. Клонируйте репозиторий:
```
git clone https://github.com/PetruschenkoEgor/parser_for_getting_information_about_online_store_products_scrapy
```
2. Установите зависимости:
```
pip install -r requirements.txt
или
poetry install
```

## Описание работы программы
- В файл alkoteka_spider.py в переменную START_URLS в виде списка необходимо вставить url для парсинга в виде списка(минимально 1 url)
- Далее перейти в директорию parser с помощью команды cd parser
- И запустить программу для парсинга командой scrapy crawl alkoteka -O result.json
- После выполнения программа создаст файл json с названием result.json и выгрузит в него основные данные по продуктам
