import os
from dblp_crawler import convert_lines, get_conferences
from database import Database

db = Database()


def main():
    data = open("journals.txt", "r")
    convert_lines(data)
    get_conferences()
    con = db.get_yearly_conference()
    for c in con:
        print(c)


if __name__ == '__main__':
    main()
