import json
import requests
from thread_database import ThreadDb
from database import Database


def get_json(url):
    page = requests.get(url)
    text = page.text
    return json.loads(text)


def process_paper(paper_title, paper_id):
    db = ThreadDb()

    base_url = "https://api.elsevier.com/content/search/scopus?query="
    api_key = "&apikey=acac2be39acb28ab1b7eef1fa53289ce&httpAccept=application/json"
    query = "TITLE(" + paper_title + ")"
    url = base_url + query + api_key

    # print(url)
    load = get_json(url)
    result = load['search-results']
    number_of_results = result["opensearch:totalResults"]
    if str(number_of_results) > "0":
        entry = result['entry'][0]
        author_link = entry['link'][1]['@href']

        affiliation_url = author_link + api_key
        # print(affiliation_url)
        load = get_json(affiliation_url)
        affiliations = load['abstracts-retrieval-response']['affiliation']

        if isinstance(affiliations, list):
            for affiliation in affiliations:
                id = affiliation['@id']
                affiliation_name = affiliation['affilname']
                country = affiliation['affiliation-country']
                print(affiliation_name)
                # db.add_affiliation(id, affiliation_name, country)
        else:
            id = affiliations['@id']
            affiliation_name = affiliations['affilname']
            country = affiliations['affiliation-country']
            print(affiliation_name)
            # db.add_affiliation(id, affiliation_name, country)

        authors = load['abstracts-retrieval-response']['authors']['author']

        if len(authors) > 1:
            for author in authors:
                user_id = author['@auid']
                first_name = author['preferred-name']['ce:given-name']
                last_name = author['preferred-name']['ce:surname']
                url = author['author-url']
                print(first_name)
                print(last_name)
                print(url)
                affiliation = author['affiliation']
                if isinstance(affiliation, list):
                    aff_id = author['affiliation'][0]['@id']
                else:
                    aff_id = author['affiliation']['@id']
                # db.add_author(user_id, first_name, last_name, url, aff_id)
                # db.add_author_paper(user_id, paper_id)
            db.put_connection()
        else:
            user_id = authors[0]['@auid']
            first_name = authors[0]['preferred-name']['ce:given-name']
            last_name = authors[0]['preferred-name']['ce:surname']
            url = authors[0]['author-url']
            affiliation = authors[0]['affiliation']
            print(first_name)
            print(last_name)
            print(url)
            if isinstance(affiliation, list):
                aff_id = authors[0]['affiliation'][0]['@id']
            else:
                aff_id = authors[0]['affiliation']['@id']

    else:
        print("No result")
        db.put_connection()


db = Database()
db.c.execute("SELECT id, title from papers where conference_id = 2 LIMIT 5")
papers = db.c.fetchall()
for paper in papers:
    id = paper[0]
    title = paper[1]
    process_paper(title, id)

# process_paper("On the Consistency of Quick Shift", 1)
