from multiprocessing import Process
import sqlite3
from math import ceil
from sys_req_lab_site import get_content
from string import ascii_lowercase

FILTERS = list(ascii_lowercase)
FILTERS.append('0-9')

con = sqlite3.connect(f"games_sys_req_site.db", timeout=50)
cursor = con.cursor()


def create_db():
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS game (
            id integer primary key autoincrement,
            name varchar(50) unique not null,
            link varchar(50) unique not null,
            image varchar(50) not null
        );
        CREATE TABLE IF NOT EXISTS requirements (
            id integer primary key autoincrement,
            game_id int not null,
            cpu varchar(100),
            ram varchar(50),
            gpu varchar(100),
            dx varchar(50),
            os varchar(100),
            sto varchar(50),
            sound varchar(100),
            CONSTRAINT fk_categories foreign key (id) references game (game_id)
        );
        """
    )
    cursor.connection.commit()

def store_game_data(data):
    cursor.execute(
        f"""
            INSERT INTO game (name, link, image) VALUES (?, ?, ?)
        """,
        (
            data.get('name'),
            data.get("link"),
            data.get("image")
        ),
    )
    cursor.connection.commit()

URL = url = f"https://gamesystemrequirements.com/database"

def extract_games(url, pagination):
    if pagination == 0:
        return
    page_url = url + f"/page/{pagination}"
    content = get_content(page_url)
    div = content.find('div', class_="main-column")
    a_tags = div.find_all('a', class_='gr_box')
    for tag in a_tags:
        data = {
            'link': tag.get("href"),
            'name': tag.get("title"),
            'image': tag.find('img').get('src'),
        }
        store_game_data(data)
    return extract_games(url, pagination-1)


def extract_games_extraction():
    list_of_processes = []
    for char in FILTERS:
        url = f"{URL}/{char}"
        content = get_content(url)
        div = content.find('div', class_="main-column")
        page_nav = div.find('div', class_='pagenav_d')
        pagination = len(page_nav.find_all('a')) if page_nav else 1
        p = Process(target=extract_games, args=(url, pagination,))
        p.start()
        list_of_processes.append(p)
    for p in list_of_processes:
        p.join()



def store_game_reqs(data):
    cursor.execute(
        f"""
            INSERT INTO requirements (game_id, cpu, ram, gpu, dx, os, sto, sound ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            data.get('game_id'),
            data.get("cpu"),
            data.get('ram'),
            data.get('gpu'),
            data.get('dx'),
            data.get('os'),
            data.get('sto'),
            data.get('sound')
        ),
    )
    cursor.connection.commit()

    
CHARACTERISTICS = ['cpu', 'ram', 'gpu', 'dx', 'os', 'sto', 'sound']
def filter_requirement(req, data_dict):
    char = req[0].rstrip(":").lower()
    value = req[1].strip()
    if char in CHARACTERISTICS:
        data_dict[char] = value 
    return data_dict


def extract_game_reqs(rows):
    for row in rows:
        content = get_content(row[1])
        reqs = content.find('div', class_='gsr_section').find_all('div', class_='gsr_row')
        data = {}
        data['game_id'] = row[0]
        print(row[0])
        for req in reqs:
            requirement = []
            requirement.append(req.find('div', class_='gsr_label').text)
            requirement.append(req.find('div', class_='gsr_text').text)
            data = filter_requirement(requirement, data)
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
    log_file = open('errors.log', 'a+')
    try:
        create_db()
        extract_games_extraction()
        execute_requirements_extraction()
    except Exception as e:
        log_file.write(f'{e}\n')
    finally:
        log_file.close()

if __name__ == "__main__":
    main()