from general import get_html
from database import Database
from nameparser import HumanName


class Worker:
    def __init__(self):
        print("Starting thread")
        self.db = Database()

    def crawl(self, conference, visited):
        url = conference[0]
        conference_id = conference[1]
        print("Crawling", conference_id)
        conference = str(conference_id)

        if conference not in visited:
            s = get_html(url)
            li = s.findAll("li", {"class": "entry inproceedings"})
            for l in li:
                divs = l.findAll("div", itemprop="headline")
                for d in divs:
                    span = d.findAll("span", itemprop="author")
                    title = d.find("span", {"class": "title"})

                    paper_title = title.text.replace(".", "")
                    print(paper_title)

                    paper_id = self.db.add_paper(paper_title, conference_id)
                    paper_id = paper_id[0]
                    print("Paper id", paper_id)

                    for sp in span:
                        name = sp.text
                        link = sp.find("a").get("href")
                        self.get_author(name, link, paper_id)
            write(str(conference_id) + "\n")
        else:
            print(str(conference_id) + " already visited!")
        return "Done!"

    def get_author(self, name, url, paper_id):
        s = get_html(url)
        n = HumanName(name)
        first_name = n.first
        middle_name = n.middle
        last_name = n.last
        is_affiliated = s.find("li", itemprop="affiliation")
        if is_affiliated:
            affiliated_to = is_affiliated.find("span", itemprop="name")
            affiliation_id = self.db.add_affiliation(affiliated_to.text)
            print("Aff id", affiliation_id[0])
            author_id = self.db.add_author(first_name, middle_name, last_name, url, affiliation_id[0])
        else:
            author_id = self.db.add_author(first_name, middle_name, last_name, url, 0)
            print("No affiliation for author with id", author_id[0])

        print("Author id", author_id[0])
        self.db.add_author_paper(author_id[0], paper_id)

