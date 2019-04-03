import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

# filenames = ['authors/aminer_authors_0.txt', 'authors/aminer_authors_1.txt', 'authors/aminer_authors_2.txt',
#              'authors/aminer_authors_3.txt', 'authors/aminer_authors_4.txt', 'authors/aminer_authors_5.txt',
#              'authors/aminer_authors_6.txt', 'authors/aminer_authors_7.txt', 'authors/aminer_authors_8.txt',
#              'authors/aminer_authors_9.txt', 'authors/aminer_authors_10.txt', 'authors/aminer_authors_11.txt',
#              'authors/aminer_authors_12.txt', 'authors/aminer_authors_13.txt', 'authors/aminer_authors_14.txt',
#              'authors/aminer_authors_15.txt', 'authors/aminer_authors_16.txt', 'authors/aminer_authors_17.txt',
#              'authors/aminer_authors_18txt', 'authors/aminer_authors_19.txt']
# with open('aminer_authors.txt', 'w') as outfile:
#     for fname in filenames:
#         with open(fname) as infile:
#             for line in infile:
#                 outfile.write(line)


link_base_aminer = "https://aminer.org/search?t=b&q="
options = webdriver.ChromeOptions()
options.add_argument('headless')
driver = webdriver.Chrome(options=options)


def get_html(url):
    page = requests.get(url)
    text = page.text
    return BeautifulSoup(text, "html.parser")

#


search_term = "Herbert Bos"
url = link_base_aminer + search_term
driver.get(url)
time.sleep(30)
print(driver.page_source)

# s = get_html(url)
# print(s.prettify())
