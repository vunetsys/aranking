from thread_database import ThreadDb
import threading
from general import get_json

filename = "docs/no_result_papers.txt"
global_lock = threading.Lock()

base_url = "https://api.elsevier.com/content/search/scopus?query="
api_key = "&apikey=6b92e885bf187016cf9ef493fbe49d74&httpAccept=application/json"


def write_no_result(paper_id):
    while global_lock.locked():
        continue

    global_lock.acquire()
    with open(filename, "a") as f:
        print("Writing no result:", paper_id)
        f.write(str(paper_id) + "\n")
        f.close()
    global_lock.release()


def parse_paper(paper_title):
    # Takes out all signs not allowed by scopus search api
    paper_title = paper_title.replace("(", "")
    paper_title = paper_title.replace(")", "")
    paper_title = paper_title.replace("%", "")
    paper_title = paper_title.replace("!", "")
    paper_title = paper_title.replace("&", "")
    paper_title = paper_title.replace("\\", "")
    paper_title = paper_title.replace("*", "")
    paper_title = paper_title.replace("#", "")
    paper_title = paper_title.replace("ϵ", "")
    paper_title = paper_title.replace("ő", "o")
    paper_title = paper_title.replace("^", "")
    paper_title = paper_title.replace("∊", "")
    paper_title = paper_title.replace("Ω", "")
    paper_title = paper_title.replace("∗", "")
    return paper_title


def get_authors(load, paper_id, database):
    try:
        authors = load['abstracts-retrieval-response']['authors']['author']
    except TypeError:
        print("Type error")
        write_no_result(paper_id)
        database.put_connection()
        return False

    if len(authors) > 1:
        for author in authors:
            user_id = author['@auid']
            first_name = author['preferred-name']['ce:given-name']
            last_name = author['preferred-name']['ce:surname']
            url = author['author-url']
            try:
                affiliation = author['affiliation']
                if isinstance(affiliation, list):
                    aff_id = author['affiliation'][0]['@id']
                else:
                    aff_id = author['affiliation']['@id']
            except KeyError:
                print("No affiliation found for author")
                aff_id = 0
                pass
            database.add_author(user_id, first_name, last_name, url, aff_id)
            database.add_author_paper(user_id, paper_id)
    else:
        user_id = authors[0]['@auid']
        first_name = authors[0]['preferred-name']['ce:given-name']
        last_name = authors[0]['preferred-name']['ce:surname']
        url = authors[0]['author-url']
        affiliation = authors[0]['affiliation']
        if isinstance(affiliation, list):
            aff_id = authors[0]['affiliation'][0]['@id']
        else:
            aff_id = authors[0]['affiliation']['@id']
        database.add_author(user_id, first_name, last_name, url, aff_id)
        database.add_author_paper(user_id, paper_id)
    database.put_connection()
    return True


def get_affiliations(affiliation_url, database):
    load = get_json(affiliation_url)

    try:
        affiliations = load['abstracts-retrieval-response']['affiliation']

        if isinstance(affiliations, list):
            for affiliation in affiliations:
                id = affiliation['@id']
                affiliation_name = affiliation['affilname']
                country = affiliation['affiliation-country']
                database.add_affiliation(id, affiliation_name, country)
        else:
            id = affiliations['@id']
            affiliation_name = affiliations['affilname']
            country = affiliations['affiliation-country']
            database.add_affiliation(id, affiliation_name, country)
    except KeyError:
        print("No affiliation found")
        pass
    return 0


def get_affiliation_url(result):
    entry = result['entry'][0]
    author_link = entry['link'][1]['@href']

    affiliation_url = author_link + api_key
    return affiliation_url


def process_paper(paper_title, paper_id):
    database = ThreadDb()
    paper_title = parse_paper(paper_title)
    print(paper_title)
    try:
        query = "TITLE(" + paper_title + ")"
        url = base_url + query + api_key

        load = get_json(url)

        result = load['search-results']
        number_of_results = result["opensearch:totalResults"]

        if str(number_of_results) > "0":
            affiliation_url = get_affiliation_url(result)
            get_affiliations(affiliation_url, database)
            return get_authors(load, paper_id, database)
        else:
            print("No results found!")
            write_no_result(paper_id)
            database.put_connection()
            return False

    except KeyError:
        print("Key Error")
        write_no_result(paper_id)
        database.put_connection()
        return False
