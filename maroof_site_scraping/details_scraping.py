import sqlite3 
from categories_scraping import load_response
from math import ceil
from multiprocessing import Process


con = sqlite3.connect('./maroof.db', timeout=200)
cursor = con.cursor()
def create_db():
    # "freeLanceDocument":{"licenseNo":"b1facbb7","nationalId":"1080992520","licenseStatus":"Active","licenseIssueDate":"2022-05-19T00:00:00","licenseExpiryDate":"2023-05-19T00:00:00","qrCode":"https://freelance.sa/certificate-validation/certificate-validation-details/b1facbb7","specialityName":"التصوير الفوتوغرافي","categoryName":"الفنون والترفية","supervisoryAuthorityName":null,"id":16444}
    # "exchangeRefundPolicy":{"hasNoRefundExchange":false,"refundDays":0,"exchangeDays":0,"exchangeRefundPolicyText":"لم يقم التاجر بإضافة سياسة للاستبدال والاسترجاع"}
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS details (
            id integer primary key autoincrement,
            shop_id integer unique not null,
            description varchar(200) not null,
            main_activity varchar(50) not null,
            cr_num int,
            cr_name varchar(50),
            region_name varchar(50),
            city_name varchar(50),
            street_name varchar(50),
            email varchar(50) ,
            mobile_no varchar(10),
            customer_service_no varchar(10),
            instagram varchar(50),
            twitter varchar(50),
            telegram varchar(50),
            whatsapp varchar(50),
            website varchar(50),
            CONSTRAINT fk_shops foreign key (id) references shop (shop_id)
        );
        '''
    )

PROVIDERS = {
    1: 'instagram',
    3: 'twitter',
    7: 'whatsapp',
    8: 'telegram',
    9: 'website'
}
def get_providers(data):
    media_links = {}
    consoles = data.get('consoles')
    for obj in consoles:
        provider = PROVIDERS.get(obj.get("providerType"))
        if provider:
            media_links[provider] = obj.get("url")
    return media_links

def store_details(data):
    media_links = get_providers(data)

    cursor.execute(
        """
            INSERT INTO details (shop_id, description, main_activity, cr_num,
            cr_name, region_name, city_name, street_name, email, mobile_no, 
            customer_service_no, instagram, twitter, telegram, whatsapp, website)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("id"),
            data.get("description"),
            data.get("mainActivity").get("name"),
            data.get('cr').get("number") if data.get("cr") else None,
            data.get('cr').get("name") if data.get("cr") else None,
            data.get("address").get("region").get("name") if data.get("address") else None,
            data.get("address").get("city").get("name") if data.get("address") else None,
            data.get("address").get('streetName') if data.get("address") else None,
            data.get("contactDetails").get("email"),
            data.get("contactDetails").get('mobile'),
            data.get("contactDetails").get('customerServiceNumber'),
            media_links.get("instagram"),
            media_links.get("twitter"),
            media_links.get("telegram"),
            media_links.get("whatsapp"),
            media_links.get("website")
        ),
    )
    cursor.connection.commit()



def extract_shop_media_data(shops_ids):
    for shop_id in shops_ids:
        url = f"https://api.thiqah.sa/maroof/public/api/app/business/{shop_id}"
        shop_content = load_response(url)
        store_details(shop_content)
        print(shop_id)

def execute_extraction():
    cursor.execute("SELECT count(id) FROM shop;")
    num_of_ids = cursor.fetchone()[0]
    extraction_processes = []
    num_of_processes = ceil(num_of_ids/100)
    for i in range(num_of_processes):
        cursor.execute("SELECT id FROM shop LIMIT ?,?;",(i*100, 100))
        shops_ids = list(map(lambda r: r[0], cursor.fetchall()))   
        p = Process(target=extract_shop_media_data, args=(shops_ids,))
        p.start()
        extraction_processes.append(p)
    for p in extraction_processes:
        p.join()

def main():
    create_db()
    execute_extraction()

if __name__ == '__main__':
    main()