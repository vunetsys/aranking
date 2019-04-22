from general import get_html

shanghai_top500 = "http://www.shanghairanking.com/ARWU2018.html"
shanghai_top1000 = "http://www.shanghairanking.com/ARWU2018Candidates.html"


def get_rankings_top500():
    s = get_html(shanghai_top500)
    tr1 = s.findAll("tr", {"class": "bgf5"})
    tr2 = s.findAll("tr", {"class": "bgfd"})

    with open("docs/shanghai500.txt", 'w') as f:
        for a in tr1:
            rank = a.find('td')
            name = a.find('a')

            f.write(rank.text + " " + name.text + "\n")

        for b in tr2:
            rank = b.find('td')
            name = b.find('a')
            f.write(rank.text + " " + name.text + "\n")
    f.close()


def get_rankings_top1000():
    s = get_html(shanghai_top1000)
    tr1 = s.findAll("tr", {"class": "bgf5"})
    tr2 = s.findAll("tr", {"class": "bgfd"})

    with open("docs/shanghai1000.txt", 'w') as f:
        for a in tr1:
            rank = a.find('td')
            name = a.find('td', {"class": "left"})
            f.write(rank.text + " " + name.text + "\n")

        for b in tr2:
            rank = b.find('td')
            name = b.find('td', {"class": "left"})
            f.write(rank.text + " " + name.text + "\n")


get_rankings_top500()
