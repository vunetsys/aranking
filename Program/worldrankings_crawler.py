from general import get_html, get_json
from database import Database
from selenium import webdriver
from bs4 import BeautifulSoup
import psycopg2 as p
import re

# USED TO GET RANKING FROM QS, SHANGHAI and THE and write them to .txt file

shanghai_top500 = "http://www.shanghairanking.com/ARWU2018.html"
shanghai_top1000 = "http://www.shanghairanking.com/ARWU2018Candidates.html"
qs_top1000 = 'https://www.topuniversities.com/sites/default/files/qs-rankings-data/357051.txt?_=1525068930958'
the_top1200 = 'https://www.timeshighereducation.com/world-university-rankings/2019/world-ranking#!/page/0/length' \
              '/-1/sort_by/rank/sort_order/asc/cols/stats'
db = Database()


def get_the():
    browser = webdriver.Chrome()
    browser.get(the_top1200)
    innerHTML = browser.execute_script("return document.body.innerHTML")
    s = BeautifulSoup(innerHTML, "html.parser")

    table = s.find('tbody')
    rows = table.findAll('tr')

    with open('/docs/the_table.txt', 'w') as f:
        for r in rows:
            rank = r.find("td", {"class": "rank sorting_1 sorting_2"})
            if "=" in rank.text:
                rank = rank.text[1:]
            else:
                rank = rank.text
            name = r.find("a", {"class": "ranking-institution-title"})

            location = r.find("div", {"class": "location"})
            country = location.find('a').text
            print(country)

            f.write(rank + " " + name.text + "\n")
            print(rank)
            print(name.text)
            print("\n")


def get_shanghai500():
    s = get_html(shanghai_top500)
    tr1 = s.findAll("tr", {"class": "bgf5"})
    tr2 = s.findAll("tr", {"class": "bgfd"})

    with open("docs/shanghai500.txt", 'w') as f:
        for a in tr1:
            rank = a.find('td')
            country_image = a.find('img').get('src')
            result = re.search('image/flag/(.*)\.png', country_image)
            country = result.group(1)
            name = a.find('a')

            if country == "USA":
                country = "United States"
            elif country == "UK":
                country = "United Kingdom"

            f.write(rank.text + " " + name.text + " - " + country + "\n")

        for b in tr2:
            rank = b.find('td')
            country_image = a.find('img').get('src')
            result = re.search('image/flag/(.*)\.png', country_image)
            country = result.group(1)
            name = b.find('a')

            if country == "USA":
                country = "United States"
            elif country == "UK":
                country = "United Kingdom"

            f.write(rank.text + " " + name.text + " - " + country + "\n")
    f.close()


def get_shanghai1000():
    s = get_html(shanghai_top1000)
    tr1 = s.findAll("tr", {"class": "bgf5"})
    tr2 = s.findAll("tr", {"class": "bgfd"})

    with open("docs/shanghai1000.txt", 'w') as f:
        for a in tr1:
            rank = a.find('td')
            name = a.find('td', {"class": "left"})
            country = a.find('img').get('title')
            f.write(rank.text + " " + name.text + " - " + country + "\n")

        for b in tr2:
            rank = b.find('td')
            name = b.find('td', {"class": "left"})
            country = b.find('img').get('title')
            f.write(rank.text + " " + name.text + " - " + country + "\n")


def get_qs1000():
    s = get_json(qs_top1000)
    rankings = s.get('data')
    with open("docs/qs1000.txt", 'w') as f:
        for uni in rankings:
            if "=" in uni['rank_display']:
                rank = str(uni['rank_display']).split('=')[-1]
            else:
                rank = str(uni['rank_display'])

            title = str(uni['title'])
            country = str(uni['country'])
            print(country)
            if "(" in title and ")" in title:
                par_index = title.index("(") - 1
                title = title[:par_index]

            f.write(rank + " " + title + " - " + country + '\n')
        f.close()


with open('docs/shanghai500.txt', 'r') as f:
    file = f.readlines()
    record = [line[:-1] for line in file]
    id = 0
    for line in record:
        uni_ranking = "".join(line.split()[:1])
        uni_from_file = " ".join(line.split()[1:])
        country = uni_from_file.split(" - ")[1]
        university = uni_from_file.split(" - ")[0]

        try:
            db.c.execute("INSERT INTO ranking_lists(id, name, shanghai_rank, country) VALUES (%s, %s, %s, %s)",
                         (id, university, uni_ranking, country))
            db.conn.commit()
            print("INSERTED: ", university)
            id += 1
        except p.IntegrityError:
            print("VALUE EXISTS")
            db.conn.rollback()
            db.c.execute("UPDATE ranking_lists SET shanghai_rank=%s WHERE name=%s", (uni_ranking, university))
            db.conn.commit()
    f.close()

with open('docs/qs1000.txt', 'r') as f:
    file = f.readlines()
    record = [line[:-1] for line in file]
    id = 1000
    for line in record:
        uni_ranking = "".join(line.split()[:1])
        uni_from_file = " ".join(line.split()[1:])
        country = uni_from_file.split(" - ")[1]
        university = uni_from_file.split(" - ")[0]

        try:
            db.c.execute("INSERT INTO ranking_lists(id, name, qs_rank, country) VALUES (%s, %s, %s, %s)",
                         (id, university, uni_ranking, country))
            db.conn.commit()
            print("INSERTED: ", university)
            id += 1
        except p.IntegrityError:
            print("VALUE EXISTS")
            db.conn.rollback()
            db.c.execute("UPDATE ranking_lists SET qs_rank=%s WHERE name=%s", (uni_ranking, university))
            db.conn.commit()
    f.close()

with open('docs/the_table.txt', 'r') as f:
    file = f.readlines()
    record = [line[:-1] for line in file]
    id = 2000
    for line in record:
        uni_ranking = "".join(line.split()[:1])
        uni_from_file = " ".join(line.split()[1:])
        try:
            db.c.execute("INSERT INTO ranking_lists(id, name, the_rank) VALUES (%s, %s, %s)", (id, uni_from_file,
                                                                                           uni_ranking))
            db.conn.commit()
            print("INSERTED: ", uni_from_file)
            id += 1
        except p.IntegrityError:
            print("VALUE EXISTS")
            db.conn.rollback()
            db.c.execute("UPDATE ranking_lists SET the_rank=%s WHERE name=%s", (uni_ranking, uni_from_file))
            db.conn.commit()
    f.close()