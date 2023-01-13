import json
from urllib import request
from urllib import error
import csv
from multiprocessing import Process, Manager

'''
{'type': 'products', 'id': '9772191979007',
'attributes': {'identifier': '2191-9798', 'productFileFormat': None,
'pricesAT': [], 'edition': None, 'title': '3R', 'unpricedItemCode': None,
'coverUrl': 'https://www.buchhandel.de/cover/9772191979007/9772191979007-cover-s.jpg',
'contributor': '', 'subTitle': 'Fachzeitschrift für sichere und effiziente Rohrleitungssysteme',
'productFormId': 'JO', 'publisher': 'Vulkan-Verlag GmbH',
'productIcon': 'journal',
'prices': [{'value': 43.0, 'country': None, 'currency': None,
'state': None, 'type': None, 'taxRate': None, 'description': None,
'minQuantity': None, 'provisional': None, 'typeQualifier': None,
'fixedRetailPrice': None, 'priceReference': False}],
'publicationDate': None, 'productType': 'journal'},
'relationships': {},
'links': {'self': '/jsonapi/products/9772191979007'}}
'''

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


def extract_data(item):
    item_id = item.get('id')
    atts = item.get('attributes')
    title = atts.get('title')
    sub_title = atts.get('subTitle')
    author = atts.get('publisher')
    image = atts.get('coverUrl')
    publish_date = atts.get('publicationDate')
    data = {
        'id':item_id,
        'title':title,
        'sub_title': sub_title,
        'author': author,
        'image_url': image,
        'publish_date': publish_date,
    }
    return data

keys = ['id', 'title', 'sub_title', 'author', 'image_url', 'publish_date']

def gather_data(items):
    books_data = []
    for item in items:
        data = extract_data(item)
        books_data.append(data)
    return books_data

def load_items(url, L):
    response = load_page(url)
    items = response.json().get('data')
    L.extend(items)

def data_scraping_process(total_elements):
    L = Manager().list()
    processes = []
    for e in range(round(total_elements/50)+1):
        url = f'https://www.buchhandel.de/jsonapi/products?filter%5Bproducts%5D%5Bquery%5D=pt%3Djournal&filter%5BkeepPage%5D=true&page%5Bnumber%5D={e+1}&page%5Bsize%5D=50&sort%5Btitle%5D=asc'
        p = Process(target=load_items, args=(url, L))
        p.start(); processes.append(p)
    for p in processes:
        p.join()
    return L


def get_total_elements():
    url = 'https://www.buchhandel.de/jsonapi/products?filter%5Bproducts%5D%5Bquery%5D=pt%3Djournal&filter%5BkeepPage%5D=true&page%5Bnumber%5D=1&page%5Bsize%5D=25&sort%5Btitle%5D=asc'
    response = load_page(url)
    json_format = get_json_format(response)
    total_elements = json_format['meta']['totalElements']
    return total_elements

def main():
    total_elements = get_total_elements()
    print(total_elements)
    items = data_scraping_process(total_elements)
    print(len(items))
    gathered_data = gather_data(items)
    with open('data.csv', 'w', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(gathered_data)

if __name__ == '__main__':
    main()
