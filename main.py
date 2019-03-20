import os
from dblp_crawler import *
from database import Database

db = Database()


def main():
    # data = open("journals.txt", "r")
    # convert_lines(data)
    # get_conferences()
    venues = db.get_venues()
    for v in venues:
        conferences = get_yearly_conferences(v[1])
        url = conferences[0][0]
        print(url)
        s = get_html(url)
        li = s.findAll("li", {"class": "entry inproceedings"})
        for l in li:
            divs = l.findAll("div", itemprop="headline")
            for d in divs:
                span = d.findAll("span", itemprop="author")
                paper_title = d.find("span", {"class": "title"})
                for sp in span:
                    name = sp.text
                    link = sp.find("a").get("href")
                    add_author(name, link, paper_title)


if __name__ == '__main__':
    main()
