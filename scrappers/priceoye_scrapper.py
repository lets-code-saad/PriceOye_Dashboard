import requests
from bs4 import BeautifulSoup
from db.db import sql_connection
from playwright.sync_api import sync_playwright

session = requests.session()
session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

conn = sql_connection()
cursor = conn.cursor()

CATEGORY_INSERT_QUERY = """
INSERT INTO category(name)
VALUES(%s)
"""

PRODUCT_INSERT_QUERY = """
INSERT INTO product(category_id,name,url)
VALUES(%s,%s,%s)
"""

VARIANT_INSERT_QUERY = """
INSERT INTO variant(product_id, colour_id, storage_id, old_price, new_price, is_available, discount, rating, reviews)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

COLOUR_INSERT_QUERY = """
INSERT INTO colour(product_id, name)
VALUES(%s,%s)
"""

STORAGE_INSERT_QUERY = """
INSERT INTO storage(product_id, ram, rom)
VALUES(%s,%s,%s)
"""


def clean_price(text):
    if not text:
        return None
    return int(text.replace("Rs", "").replace(",", "").strip())


def variants_scrapper(variant_url, browser):
    print(f"Scrapping {variant_url}...")
    variants = []

    page = browser.new_page()
    page.goto(variant_url, timeout=30000)
    page.wait_for_load_state("networkidle")

    colour_elements = page.query_selector_all("ul.colors li")
    if not colour_elements:
        colour_elements = [None]

    storage_elements = page.query_selector_all("ul.sizes li")
    if not storage_elements:
        storage_elements = [None]

    for colour in colour_elements:
        if colour:
            colour.click()
            page.wait_for_selector("span.summary-price")
            colour_name = colour.inner_text().strip()
            colour_availibility = not colour.query_selector("span.sold-out-tag")
        else:
            colour_name = None
            colour_availibility = True

        for storage in storage_elements:
            if storage:
                storage.click()
                page.wait_for_selector("span.summary-price")
                storage_text = storage.inner_text().strip().upper()
                storage_availibility = not storage.query_selector("span.sold-out-tag")
            else:
                storage_text = "STANDARD"
                storage_availibility = True

            ram = None
            rom = None

            if storage_text not in ("STANDARD", "DEFAULT", "-", "—"):
                storage_parts = storage_text.split("-")

                if len(storage_parts) >= 1:
                    rom_part = (
                        storage_parts[0].replace("GB", "").replace("ROM", "").strip()
                    )
                    if rom_part.isdigit():
                        rom = int(rom_part)

                if len(storage_parts) >= 2:
                    ram_part = (
                        storage_parts[1].replace("GB", "").replace("RAM", "").strip()
                    )
                    if ram_part.isdigit():
                        ram = int(ram_part)

            new_price_tag = page.query_selector("span.summary-price")
            new_price_text = new_price_tag.inner_text() if new_price_tag else None

            old_price_el = page.query_selector("div.retail-price")
            old_price_text = old_price_el.inner_text() if old_price_el else None

            discount_el = page.query_selector("span.save-price")
            discount_text = (
                discount_el.inner_text().replace("%", "").replace("OFF", "").strip()
                if discount_el
                else None
            )
            discount = (
                int(discount_text)
                if discount_text and discount_text.isdigit()
                else None
            )

            # RATING
            rating_section = page.query_selector("div.po-rating-section")
            rating_string = (
                page.query_selector("div.semi-bold.rating-points").inner_text().strip()
                if rating_section and page.query_selector("div.semi-bold.rating-points")
                else None
            )
            rating = float(rating_string) if rating_string else None

            # REVIEWS
            reviews_string = (
                page.query_selector("div.semi-bold.rating-count")
                .inner_text()
                .replace("Reviews", "")
                .strip()
                if rating_section and page.query_selector("div.semi-bold.rating-count")
                else None
            )
            reviews = (
                int(reviews_string)
                if reviews_string and reviews_string.isdigit()
                else None
            )

            variants.append(
                {
                    "colour_name": colour_name,
                    "ram": ram,
                    "rom": rom,
                    "old_price": clean_price(old_price_text),
                    "new_price": clean_price(new_price_text),
                    "discount": discount,
                    "is_available": colour_availibility and storage_availibility,
                    "rating": rating,
                    "reviews": reviews,
                }
            )

    page.close()
    return variants


def all_categories_scrapper(category_url, category_name, browser):
    page_number = 1
    cursor.execute(CATEGORY_INSERT_QUERY, (category_name,))
    category_id = cursor.lastrowid
    print(f"Scrapping Category {category_name}...")

    while True:
        response = session.get(f"{category_url}?page={page_number}")
        soup = BeautifulSoup(response.text, "html.parser")

        products_container = soup.find_all("div", class_="productBox")
        if not products_container:
            break

        for product in products_container:
            try:
                name = product.find("div", class_="text-box").get_text(strip=True)

                url_tag = product.find("a", class_="ga-dataset")
                url = url_tag.get("href") if url_tag else None
                if not url:
                    continue

                variant_details = variants_scrapper(url, browser)
                if not variant_details:
                    continue

                cursor.execute(PRODUCT_INSERT_QUERY, (category_id, name, url))
                product_id = cursor.lastrowid

                for variant in variant_details:
                    cursor.execute(
                        COLOUR_INSERT_QUERY, (product_id, variant["colour_name"])
                    )
                    colour_id = cursor.lastrowid

                    cursor.execute(
                        STORAGE_INSERT_QUERY,
                        (product_id, variant["ram"], variant["rom"]),
                    )
                    storage_id = cursor.lastrowid

                    cursor.execute(
                        VARIANT_INSERT_QUERY,
                        (
                            product_id,
                            colour_id,
                            storage_id,
                            variant["old_price"],
                            variant["new_price"],
                            variant["is_available"],
                            variant["discount"],
                            variant["rating"],
                            variant["reviews"],
                        ),
                    )

                conn.commit()

            except Exception as e:
                print("DB ERROR", e)
                conn.rollback()
                continue

        page_number += 1

    print("Website Scrapped Successfully!")


def get_categories_links(base_page_url, browser):
    response = session.get(base_page_url)
    if response:
        soup = BeautifulSoup(response.text, "html.parser")
        categories_links = soup.find_all("a", class_="categoryCard")
        for link in categories_links:
            url = link.get("href")
            if url and url.startswith("https"):
                category = url.rstrip("/").split("/")[-1].replace("-", " ").title()
                all_categories_scrapper(url, category, browser)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    get_categories_links("https://priceoye.pk/", browser)
    browser.close()
