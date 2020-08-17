"""Программа для парсинга списка игр с metacritic.com 
по заданной ссылке (на игры для пк или консолей)

"""

import requests
from bs4 import BeautifulSoup
import csv
import os
from time import sleep
from random import randint


URLS = {
    '1' : 'https://www.metacritic.com/browse/games/score/userscore/all/ps4/filtered?sort=desc',
    '2' : 'https://www.metacritic.com/browse/games/score/userscore/all/xboxone/filtered?sort=desc',
    '3' : 'https://www.metacritic.com/browse/games/score/userscore/all/pc/filtered?sort=desc',
    '4' : 'https://www.metacritic.com/browse/games/score/userscore/all/switch/filtered?sort=desc',
    '5' : 'https://www.metacritic.com/browse/games/score/userscore/all/wii-u/filtered?sort=desc',
    '6' : 'https://www.metacritic.com/browse/games/score/userscore/all/3ds/filtered?sort=desc',
    '7' : 'https://www.metacritic.com/browse/games/score/userscore/all/vita/filtered?sort=desc',
    '8' : 'https://www.metacritic.com/browse/games/score/userscore/all/ios/filtered?sort=desc',
    '9' : 'https://www.metacritic.com/browse/games/score/userscore/all/stadia/filtered?sort=desc',
    '10' : 'https://www.metacritic.com/browse/games/score/userscore/all/xbox-series-x/filtered?sort=desc',
    '11' : 'https://www.metacritic.com/browse/games/score/userscore/all/ps5/filtered?sort=desc'
    }
HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.44',
    'accept': '*/*'
    }
HOST = 'https://www.metacritic.com'
FILE = 'games.csv'

def save_file(items, path):
    """Функция сохранения файла. Принимает предметы и путь.

    """
    with open(path, 'w', newline='') as file:
        #delimiter - разделитель строк в файле
        writer = csv.writer(file, delimiter=';')
        writer.writerow([
            'Название', 'Ссылка', 'Оценка пользователей', 'Дата релиза'
            ])
        for item in items:
            writer.writerow([
                item['title'], item['link'], item['user_score'],
                item['release_date']
                ])

def get_html(url, params=None):
    """Функция для отправки get запроса на основе модуля requests.
    Принимает ссылку и параметры(по умолчанию - None).
    Возвращает метод get.
    
    """
    r = requests.get(url, headers=HEADERS, params=params)
    return r

def get_pages_count(html):
    """Функция для получения количества страниц с контентом.
    Находит класс 'page_num' с тэгом 'a'.
    При нахождении таких классов выдаёт кол-во страниц.
    В противном случае кол-во страниц = 1.
    
    """
    soup = BeautifulSoup(html, 'html.parser')
    pages = soup.find_all('a', class_='page_num')
    if pages:
        return int(pages[-1].get_text())
    else:
        return 1
    print(pages)

def get_content(html):
    """Функция получения контента. Принимает значение аргумента html.
    Находит список классов class_ с названием продукта с тэгом 'li'.0
    Далее для каждого продукта добавляет в список games словари
    с названием, ссылкой, оценкой пользователей, датой релиза.
    Возвращает список словарей games.
    
    """
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find('div', class_='title_bump')\
        .find_all('td', class_='clamp-summary-wrap')
    games = []
    for item in items:
        # Пропуск всех <div class="platform"> для доступа к дате релиза игр
        item.find('div', class_='clamp-details')\
            .find_next('div', class_='platform').decompose()
        games.append({
            #strip - метод get text, обрезающий отступы
            'title': item.find('a', class_='title').find_next('h3')\
                .get_text(strip=True),
            #метод get с атрибутом href передаёт ссылку
            'link': HOST + item.find('a', class_='title').get('href'), 
            'user_score': item.find('div', class_='clamp-score-wrap')\
                .find_next('div').get_text().replace('.', ','),
            # find_next() позволяет найти ветки внутри уже найденной
            'release_date': item.find('div', class_='clamp-details')\
            .find_next('span').get_text()
            })
    
    return games


def parse():
    """Функция парсинга с запуском записанного файла. Обрабатывает 
    введённую ссылку функцией get_html().
    При статусе запроса 200 создаёт пустой список игр games 
    и получает кол-во страниц контента функцией get_pages_count()
    в текстовой форме.
    Для каждой страницы отправляет get запрос с ссылкой и
    параметрами страницы.
    Расширяет список games списком-резултьатом работы функции.
    Задержка 1-10 секунд.
    Как итог - сохранение функцией save_file с параметрами games
    и названием файла согласно аргумента FILE.
    
    """
    URL = URLS[input(
        'Игровые платформы: \n1. PS4; \n2. Xbox One; \n3. PC; \n4. Switch;\
            \n5. Wii U; \n6. 3DS; \n7. PS Vita; \n8. iOS; \n9. Stadia;\
            \n10. Xbox Series X; \n11. PS5. \nВведите номер нужной платформы: '
        )]
    html = get_html(URL)
    if html.status_code == 200:
        games = []
        pages_count = get_pages_count(html.text)
        for page in range(pages_count):
            print(f'Парсинг страницы {page +1} из {pages_count}')
            html = get_html(URL, params={'page': page})
            games.extend(get_content(html.text))
            #подбор значения задержки
            stumble = randint(1, 10)
            #задержка в обработке на stumble секунд
            sleep(stumble)
        save_file(games, FILE)
        print(f'Получено {len(games)} игр.')
        os.startfile(FILE)
    else:
        print('Error')


parse()