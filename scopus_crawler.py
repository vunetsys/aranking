import json
import requests
from thread_database import ThreadDb
import threading
import logging

filename = "no_result_papers.txt"
global_lock = threading.Lock()


def write_no_result(paper_id):
    while global_lock.locked():
        continue

    global_lock.acquire()
    with open(filename, "a") as f:
        print("Writing:", paper_id)
        f.write(str(paper_id) + "\n")
        f.close()
    global_lock.release()


def get_json(url):
    page = requests.get(url)
    # print(page.headers)
    text = page.text
    return json.loads(text)


def process_paper(paper_title, paper_id):
    database = ThreadDb()
    try:
        base_url = "https://api.elsevier.com/content/search/scopus?query="
        # api_key = "&apikey=acac2be39acb28ab1b7eef1fa53289ce&httpAccept=application/json"
        api_key = "&apikey=3e6495a4f1db49837a07d3c615779ae4&httpAccept=application/json"
        query = "TITLE(" + paper_title + ")"
        url = base_url + query + api_key
        load = get_json(url)
        result = load['search-results']
        number_of_results = result["opensearch:totalResults"]

        if str(number_of_results) > "0":
            entry = result['entry'][0]
            author_link = entry['link'][1]['@href']

            affiliation_url = author_link + api_key
            print(affiliation_url)
            load = get_json(affiliation_url)
            affiliations = load['abstracts-retrieval-response']['affiliation']

            if isinstance(affiliations, list):
                for affiliation in affiliations:
                    id = affiliation['@id']
                    affiliation_name = affiliation['affilname']
                    country = affiliation['affiliation-country']
                    print(id)
                    print(affiliation_name)
                    print(country)
                    database.add_affiliation(id, affiliation_name, country)
            else:
                id = affiliations['@id']
                affiliation_name = affiliations['affilname']
                country = affiliations['affiliation-country']
                print(id)
                print(affiliation_name)
                print(country)
                database.add_affiliation(id, affiliation_name, country)

            authors = load['abstracts-retrieval-response']['authors']['author']

            if len(authors) > 1:
                for author in authors:
                    user_id = author['@auid']
                    first_name = author['preferred-name']['ce:given-name']
                    last_name = author['preferred-name']['ce:surname']
                    url = author['author-url']
                    print(user_id)
                    print(first_name)
                    print(last_name)
                    print(url)
                    affiliation = author['affiliation']
                    if isinstance(affiliation, list):
                        aff_id = author['affiliation'][0]['@id']
                        print(aff_id)
                    else:
                        aff_id = author['affiliation']['@id']
                        print(aff_id)
                    database.add_author(user_id, first_name, last_name, url, aff_id)
                    database.add_author_paper(user_id, paper_id)
            else:
                user_id = authors[0]['@auid']
                first_name = authors[0]['preferred-name']['ce:given-name']
                last_name = authors[0]['preferred-name']['ce:surname']
                url = authors[0]['author-url']
                affiliation = authors[0]['affiliation']
                print(user_id)
                print(first_name)
                print(last_name)
                print(url)
                if isinstance(affiliation, list):
                    aff_id = authors[0]['affiliation'][0]['@id']
                    print(aff_id)
                else:
                    aff_id = authors[0]['affiliation']['@id']
                    print(aff_id)
                database.add_author(user_id, first_name, last_name, url, aff_id)
                database.add_author_paper(user_id, paper_id)
            database.put_connection()
            return True
        else:
            print("No result")
            write_no_result(paper_id)
            database.put_connection()
            return False
    except KeyError:
        database.put_connection()
        # logging.exception("message")
        return False
# #
# db = Database()
# db.c.execute("SELECT id, title from papers where conference_id = 3 LIMIT 5")
# papers = db.c.fetchall()
# for paper in papers:
#     id = paper[0]
#     title = paper[1]
#     process_paper(title, id)
