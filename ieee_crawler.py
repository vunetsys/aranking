from general import get_html

link_base_ieee = "https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText="
api_key = "qfyrt56natmrxkbwsneunrqw"


def get_ieee_author(title, paper_id, db):
    url = link_base_ieee + title
    s = get_html(url)


