import sqlite3
from multiprocessing import Manager, Process
import requests
from bs4 import BeautifulSoup as bs


con = sqlite3.connect("maroof.db", timeout=200)
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
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS shop (
            id primary key not null,
            name_ar varchar(50) unique,
            name_en varchar(50), 
            rating real,
            rating_num integer,
            cr_number integer,
            about_business text,
            image_link varchar(100), 
            cat_id integer,
            CONSTRAINT fk_categories foreign key (id) references category (cat_id)
        );"""
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS personal_data (
            id integer primary key autoincrement,
            email varchar(50) ,
            mobile_no varchar(10), 
            tel_no varchar(10),
            instagram varchar(50),
            twitter varchar(50),
            telegram varchar(50),
            whatsapp varchar,
            shop_id integer,
            CONSTRAINT fk_shops foreign key (id) references shop (shop_id)
        );"""
    )
    cursor.connection.commit()


def insert_into_category_table(data):
    cursor.execute(
        f"""
            INSERT INTO category (id, name, num_of_shops) VALUES (?, ?, ?)
        """,
        (data["id"], data["name"], data["num_of_shops"]),
    )
    cursor.connection.commit()


def read_page(url):
    content = requests.get(url)
    if content.status_code != 200:
        exit(1)
    soup = bs(content.text, "lxml")
    return soup


def get_categories(home_content):
    cat_container = home_content.find(id="myTab")
    cats = cat_container.find_all("li")
    return cats

CATEGORIES_IDS = set()

def get_category_data(cat):
    cat_id = int(cat.find("a").get("id").split("-")[0])
    name = cat.find("h3").text
    num_of_shops = int(cat.find("h4").text.split()[0])
    CATEGORIES_IDS.add(cat_id)
    data = {"id": cat_id, "name": name, "num_of_shops": num_of_shops}
    return data


def store_categories_data(cats):
    for cat in cats:
        data = get_category_data(cat)
        insert_into_category_table(data)


def get_category_json_shops(cat_id):
    url = f"https://maroof.sa/BusinessType/MoreBusinessList?businessTypeId={cat_id}&pageNumber=0&sortProperty=BestRating&desc=True"
    content = requests.get(url)
    if content.status_code != 200:
        print("wrong process")
        exit(1)
    return content.json()


def store_shop_data(data):
    cursor.execute(
        f"""
            INSERT INTO shop (id, name_ar, name_en, rating, rating_num, cr_number,
            about_business, image_link, cat_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("Id"),
            data.get("NameAr"),
            data.get("Name"),
            data.get("Rating"),
            data.get("RatingNum"),
            data.get("CRNumber"),
            data.get("DescriptionArSummary"),
            data.get("MainImageUrl"),
            data.get("cat_id"),
        ),
    )
    cursor.connection.commit()


def get_shops_data(cat_id, L):
    json_data = get_category_json_shops(cat_id)
    shops_list = json_data.get("Businesses")
    for shop in shops_list:
        shop["cat_id"] = cat_id
        store_shop_data(shop)
        shop_id = shop.get("Id")
        print(shop_id)
        L.append(shop_id)


def perform_processes(ids, func):
    L = Manager().list()
    processes = []
    for _id in ids:
        p = Process(target=func, args=(_id, L))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    return L


def classify_links(a_s):
    data = {}
    for a in a_s:
        href = a["href"]
        print(href)
        if href.__contains__("mailto:"):
            data["email"] = href.split(":")[1]
        elif href.__contains__("tel:"):
            num = href.split(":")[1]
            if len(num) == 9:
                data["tel_no"] = num
            data["mobile_no"] = num
        elif href.__contains__("instagram"):
            data["instagram"] = href
        elif href.__contains__("twitter"):
            data["twitter"] = href
        elif href.__contains__("wa.me"):
            data["whatsapp"] = href
        elif any(i in href for i in ["t.me", "telegram"]):
            data["telegram"] = href
    return data


def classify_shop_details(divs):
    data = {}
    for row in divs:
        a_s = row.find_all("a")
        links_dict = classify_links(a_s)
        data.update(links_dict)
    return data


def get_shop_personal_data(shop_id, L):
    url = f"https://maroof.sa/{shop_id}"
    try:
        shop_content = read_page(url)
    except:
        return
    body = shop_content.find_all(id="page-content")[1]
    comm_details = body.find_all("div", attrs={"class": "row"})[1:4:2]
    print("inner")
    data = classify_shop_details(comm_details)
    data["shop_id"] = shop_id
    store_communication_details(data)


def store_communication_details(data):
    print(data)
    cursor.execute(
        """
            INSERT INTO personal_data (email, mobile_no, tel_no, instagram, twitter,
            telegram, whatsapp, shop_id) values (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("email"),
            data.get("mobile_no"),
            data.get("tel_no"),
            data.get("instagram"),
            data.get("twitter"),
            data.get("telegram"),
            data.get("whatsapp"),
            data.get("shop_id"),
        ),
    )
    cursor.connection.commit()


def extract_data(url):
    page = read_page(url)
    categories = get_categories(page)
    store_categories_data(categories)
    shops_ids = perform_processes(CATEGORIES_IDS, get_shops_data)
    print(shops_ids)
    perform_processes(shops_ids, get_shop_personal_data)


def main():
    create_db()
    extract_data("https://maroof.sa")


if __name__ == "__main__":
    main()
    con.close()
    print(CATEGORIES_IDS)
