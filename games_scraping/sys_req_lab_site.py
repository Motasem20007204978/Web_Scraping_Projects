from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from multiprocessing import Process
import sqlite3
from math import ceil

con = sqlite3.connect(f"sys_req_lab_site.db", timeout=50)
cursor = con.cursor()


def create_db():
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS game (
            id integer primary key autoincrement,
            name varchar(50) not null,
            link varchar(50) unique not null
        );
        CREATE TABLE IF NOT EXISTS requirements (
            id integer primary key autoincrement,
            game_id int not null,
            cpu varchar(50),
            ram varchar(50),
            vid_card varchar(50) ,
            dedicated_vid_ram varchar(50),
            pixel_shared real,
            vertex_shared real,
            os varchar(50),
            free_space varchar(50),
            sound_card varchar(50),
            CONSTRAINT fk_categories foreign key (id) references game (game_id)
        );
        """
    )
    cursor.connection.commit()

def get_content(url):
    content = urlopen(url, timeout=50)
    soup = bs(content, 'lxml')
    return soup 

def store_game_data(data):
    cursor.execute(
        f"""
            INSERT INTO game (name, link) VALUES (?, ?)
        """,
        (
            data.get('name'),
            data.get("link")
        ),
    )
    cursor.connection.commit()

def extract_games_data(content):
    a_tags = content.find('ul', class_='list-unstyled').find_all('a')
    for tag in a_tags:
        data = {
            'name': tag.text,
            'link': 'https://www.systemrequirementslab.com' + tag.get("href")
        }
        print(data['name'])
        store_game_data(data)


def store_game_reqs(data):
    cursor.execute(
        f"""
            INSERT INTO requirements (game_id, cpu, ram, vid_card, 
            dedicated_vid_ram, pixel_shared, vertex_shared, os, free_space, 
            sound_card) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get('game_id'),
            data.get("cpu"),
            data.get('ram'),
            data.get('vid_card'),
            data.get('dedicated_vid_ram'),
            data.get('pixel_shared'),
            data.get('vertex_shared'),
            data.get('os'),
            data.get('free_space'),
            data.get('sound_card')
        ),
    )
    cursor.connection.commit()

def filter_requirement(req, data_dict):
    value = req[1].strip()
    if req[0] == 'CPU':
        data_dict['cpu'] = value 
    elif req[0] == 'RAM':
        data_dict['ram'] = value 
    elif req[0] == 'VIDEO CARD':
        data_dict['vid_card'] = value 
    elif req[0] == 'DEDICATED VIDEO RAM':
        data_dict['dedicated_vid_ram'] = value 
    elif req[0] == 'PIXEL SHADER':
        data_dict['pixel_shared'] = value 
    elif req[0] == 'VERTEX SHADER':
        data_dict['vertex_shared'] = value 
    elif req[0] == 'OS':
        data_dict['os'] = value 
    elif req[0] == 'FREE DISK SPACE':
        data_dict['free_space'] = value 
    elif req[0] == 'SOUND CARD':
        data_dict['sound_card'] = value 
    return data_dict


def extract_game_reqs(rows):
    for row in rows:
        content = get_content(row[1])
        reqs = content.find('div', class_='container').find('ul').find_all('li')
        data = {}
        data['game_id'] = row[0]
        print(row[0])
        for req in reqs:
            data = filter_requirement(req.text.rsplit(":"), data)
        store_game_reqs(data)

def execute_requirements_extraction():
    cursor.execute("SELECT count(id) FROM game;")
    num_of_games = cursor.fetchone()[0]
    extraction_processes = []
    num_of_processes = ceil(num_of_games/50)
    for i in range(num_of_processes):
        cursor.execute("SELECT id, link FROM game LIMIT ?,?;",(i*50, 50))
        rows = cursor.fetchall()
        p = Process(target=extract_game_reqs, args=(rows,))
        p.start()
        extraction_processes.append(p)
    for p in extraction_processes:
        p.join()

def main():
    create_db()
    url = 'https://www.systemrequirementslab.com/all-games-list/'
    content = get_content(url)
    extract_games_data(content)
    execute_requirements_extraction()

if __name__ == "__main__":
    main()