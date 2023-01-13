import sqlite3
from urllib import request
from urllib import error
import json
from bs4 import BeautifulSoup as bs
import subprocess

con = sqlite3.connect(f"./dbs/maroof.db", timeout=200)
cursor = con.cursor()


def create_db():
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS category (
            id int primary key not null,
            name varchar(50) unique not null,
            num_of_shops integer not null
        );"""
    )
    cursor.connection.commit()


def load_page(url):
    try:
        req = request.Request(url)
        response = request.urlopen(req, timeout=10)
    except error.HTTPError as e:
        print(e)
        exit(1)
    except error.URLError as e:
        print(e)
        exit(1)
    return response

def get_json_format(response):
    r = response.read().decode('utf-8')
    json_content = json.loads(r)
    return json_content

def store_category_data(data):
    cursor.execute(
        f"""
            INSERT INTO category (id, name, num_of_shops) VALUES (?, ?, ?)
        """,
        (data["id"], data["name"], data["num_of_shops"]),
    )
    cursor.connection.commit()


def read_page(url):
    content = load_page(url)
    soup = bs(content.read().decode('utf-8'), "lxml")
    return soup


def load_categories_content(home_content):
    cat_container = home_content.find(id="myTab")
    cats = cat_container.find_all("li")
    return cats

CATEGORIES= dict()

def extract_category_data(cat):
    cat_id = int(cat.find("a").get("id").split("-")[0])
    name = cat.find("h3").text
    num_of_shops = int(cat.find("h4").text.split()[0])
    CATEGORIES[cat_id] = num_of_shops
    data = {"id": cat_id, "name": name, "num_of_shops": num_of_shops}
    return data

def maroof_site_scraping(url="https://maroof.sa"):
    page = read_page(url)

    categories = load_categories_content(page)
    for cat in categories:
        data = extract_category_data(cat)
        store_category_data(data)
    
    for _id, num_of_shops in CATEGORIES.items():
        subprocess.run(['python', './shops_scraping.py', _id, num_of_shops])

def main():
    create_db()
    maroof_site_scraping()

if __name__ == '__name__':
    main()