from googleapiclient.discovery import build

my_api_key = ""
my_cse_id = "005296326583044659583:xsrnrd7nqiw"

# Input: search term
# Will return a list of found items through the Google Search API


def google_search(search_term, api_key=my_api_key, cse_id=my_cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']
