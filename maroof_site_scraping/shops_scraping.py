import sqlite3
from multiprocessing import Process, current_process
from main import load_page, read_page, get_json_format
import sys 

con = sqlite3.connect(f"./dbs/cat-id-{sys.argv[1]}.db", timeout=200)
cursor = con.cursor()


def create_db():
    cursor.executescript(
        """
        ATTACH DATABASE './dbs/maroof.db' as catdb;
        CREATE TABLE IF NOT EXISTS shop (
            id primary key not null,
            name_ar varchar(50),
            name_en varchar(50),
            rating real,
            rating_num integer,
            cr_number integer,
            about_business text,
            image_link varchar(100),
            cat_id integer,
            CONSTRAINT fk_categories foreign key (id) references category (cat_id)
        );
        CREATE TABLE IF NOT EXISTS media_information (
            id integer primary key autoincrement,
            email varchar(50) ,
            mobile_no varchar(10),
            tel_no varchar(10),
            facebook varchar(50),
            instagram varchar(50),
            twitter varchar(50),
            telegram varchar(50),
            whatsapp varchar,
            shop_id integer unique not null,
            CONSTRAINT fk_shops foreign key (id) references shop (shop_id)
        );"""
    )
    cursor.connection.commit()


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


def classify_links(a_s):
    data = {}
    for a in a_s:
        href = a["href"]
        if href.__contains__("mailto:"):
            data["email"] = href.split(":")[1]
        elif href.__contains__("tel:"):
            num = href.split(":")[1]
            if len(num) == 9:
                data["tel_no"] = num
            else:
                data["mobile_no"] = num
        elif href.__contains__('facebook'):
            data['facebook'] = href
        elif href.__contains__("instagram"):
            data["instagram"] = href
        elif href.__contains__("twitter"):
            data["twitter"] = href
        elif href.__contains__("wa.me"):
            data["whatsapp"] = href
        elif any(i in href for i in ["t.me", "telegram"]):
            data["telegram"] = href
    return data


def classify_shop_media_data(divs):
    data = {}
    for row in divs:
        a_s = row.find_all("a")
        links_dict = classify_links(a_s)
        data.update(links_dict)
    return data


def store_media_data(data):
    cursor.execute(
        """
            INSERT INTO media_information (email, mobile_no, tel_no, facebook,
            instagram, twitter, telegram, whatsapp, shop_id)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("email"),
            data.get("mobile_no"),
            data.get("tel_no"),
            data.get('facebook'),
            data.get("instagram"),
            data.get("twitter"),
            data.get("telegram"),
            data.get("whatsapp"),
            data.get("shop_id"),
        ),
    )
    cursor.connection.commit()


def extract_shop_media_data(shop_id):
    url = f"https://maroof.sa/{shop_id}"
    shop_content = read_page(url)
    body = shop_content.find_all(id="page-content")[1]
    media_data = body.find_all("div", attrs={"class": "row"})[1:4:2]
    data = classify_shop_media_data(media_data)
    data["shop_id"] = shop_id
    store_media_data(data)

def store_shops_data(cat_id, shops_list):
    for shop in shops_list:
        shop["cat_id"] = cat_id
        store_shop_data(shop)
        shop_id = shop.get("Id")
        print(shop_id, current_process().name)
        extract_shop_media_data(shop_id)


def get_category_shops(cat_id, start_page, end_page):
    url = f"https://maroof.sa/BusinessType/MoreBusinessList?businessTypeId={cat_id}&pageNumber={start_page}&sortProperty=BestRating&desc=True"
    content = load_page(url)
    json_data = get_json_format(content)
    businesses = json_data.get('Businesses')
    store_shops_data(cat_id, businesses)
    if start_page > end_page:
        return
    return get_category_shops(cat_id, start_page+1, end_page)


def extract_shops_by_category(cat_id, num_of_shops):
    extraction_processes = []
    num_of_processes = round(num_of_shops/100)
    for i in range(num_of_processes):
        start_page = i*10; end_page = start_page+9
        p = Process(target=get_category_shops, args=(cat_id, start_page, end_page))
        p.start()
        extraction_processes.append(p)
    for p in extraction_processes:
        p.join()

def main():
    create_db()
    extract_shops_by_category(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
    con.close()
