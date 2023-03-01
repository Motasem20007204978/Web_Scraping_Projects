import sqlite3 
from multiprocessing import Process, current_process
import json
from categories_scraping import load_response
from math import ceil


con = sqlite3.connect('./maroof.db', timeout=200)
cur = con.cursor()
def create_db():

    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS shop (
            id primary key not null,
            user_id not null,
            name_ar varchar(50),
            name_en varchar(50),
            rating real,
            rating_num integer,
            image_link varchar(100),
            cat_id integer,
            subcat_id integer,
            CONSTRAINT fk_categories foreign key (id) references category (cat_id),
            CONSTRAINT fk_subcategories foreign key (id) references subcategory (subcat_id)
        );
        '''
    )


def store_shop_data(data):
    cur.execute(
        f"""
            INSERT INTO shop (id, user_id, name_ar, name_en, rating, 
            rating_num, image_link, cat_id, subcat_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("id"),
            data.get("userId"),
            data.get("nameAr"),
            data.get("name"),
            data.get("rating"),
            data.get("totalReviews"),
            data.get("imageUrl"),
            data['businessType'].get('id'),
            data['businessSubType'].get('id') if data.get("businessSubType") else None,
        ),
    )
    cur.connection.commit()


def store_shops_data(shops_list):
    for shop in shops_list:
        store_shop_data(shop)
        shop_id = shop.get("id")
        print(shop_id, current_process().name)


def get_range_of_shops(skip_count, max_count):
    if skip_count == max_count:
        return
    url = f"https://api.thiqah.sa/maroof/public/api/app/business/search?sortBy=2&sortDirection=2&skipCount={skip_count}&maxResultCount=50"
    content = load_response(url)
    objects = content.get('items')
    store_shops_data(objects)
    return get_range_of_shops(skip_count+50, max_count)


def extract_shops():
    extraction_processes = []
    url = f"https://api.thiqah.sa/maroof/public/api/app/business/search?sortBy=2&sortDirection=2&skipCount=0&maxResultCount=1"
    response = load_response(url)
    total_count = response.get("totalCount")
    num_of_processes = ceil(total_count/1000)
    for i in range(num_of_processes):
        skip_count = i*1000; max_count = skip_count+1000
        p = Process(target=get_range_of_shops, args=(skip_count, max_count))
        p.start()
        extraction_processes.append(p)
    for p in extraction_processes:
        p.join()


def main():
    create_db()
    extract_shops()

if __name__ == '__main__':
    main()