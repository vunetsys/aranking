import os
from dblp_crawler import convert_lines, get_conferences
from database import Database

db = Database()


def main():
    # if os.path.isfile('./database.txt'):
    #     f = open('database.txt', 'r')
    #     count = 0
    #     for line in f:
    #         count += 1
    #         if count % 2 == 0:
    #             get_conferences(line)
    #     f.close()
    # data = open("journals.txt", "r")
    # convert_lines(data)
    # get_conferences()
    con = db.get_yearly_conference()
    for c in con:
        print(c)


if __name__ == '__main__':
    main()
