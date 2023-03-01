import sqlite3
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import json

con = sqlite3.connect(f"maroof.db", timeout=200)
cursor = con.cursor()


def create_db():
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS category (
            id int primary key not null,
            type_id int unique not null,
            name varchar(50) unique not null,
            key varchar(50) unique not null,
            icon varchar(50) unique not null
        );
        CREATE TABLE IF NOT EXISTS subcategory (
            id int primary key not null,
            cat_id integer,
            name varchar(50) not null,
            key varchar(50) not null,
            CONSTRAINT fk_categories foreign key (id) references category (cat_id)
        );
        """
    )
    cursor.connection.commit()


def store_category_data(data):
    cursor.execute(
        f"""
            INSERT INTO category (id, type_id, name, key, icon) VALUES (?, ?, ?, ?, ?)
        """,
        (data["id"], data["typeCategoryId"], data["name"], data["key"], data['icon']),
    )
    cursor.connection.commit()


def store_subcategory_data(data):
    cursor.execute(
        f"""
            INSERT INTO subcategory (id, cat_id, name, key) VALUES (?, ?, ?, ?)
        """,
        (data["id"], data["businessTypeId"], data["name"], data["key"]),
    )
    cursor.connection.commit()


def load_response(url):
    headers = {
        'apiKey': 'c1qesecmag8GSbxTHGRjfnMFBzAH7UAN',
        "Access-Control-Request-Headers": "apikey,content-type",
        'Content-type': 'Application/json',
        "Host": "api.thiqah.sa",
        'Origin': 'https://maroof.sa/',
        'Referer': 'https://maroof.sa/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0'
    }
    try:
        request = Request(url=url, headers=headers)
        response = urlopen(request, timeout=50)
    except HTTPError as e:
        print(e)
        exit(1)
    except URLError as e:
        print(e)
        exit(1)
    return json.loads(response.read().decode('utf-8'))


def extract_categories(url):
    data = load_response(url)
    for obj in data:
        store_category_data(obj)
        extract_subcategories(obj["id"])
        

def extract_subcategories(cat_id):
    url = f"https://api.thiqah.sa/maroof/public/api/app/business-type/sub-types?businessTypeid={cat_id}&isActive=true"
    data = load_response(url)
    for obj in data:
        store_subcategory_data(obj)

def main():
    create_db()
    cats_url = "https://api.thiqah.sa/maroof/public/api/app/business-type/types?isActive=true"
    extract_categories(cats_url)

if __name__ == '__main__':
    main()