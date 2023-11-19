import json
import requests

REQUESTS_USERAGENT = 'Confluence DEX Token Discovery 0.0.1'

CONFLUENCEDEX_LISTINGS_URL = "https://rawgit.com/confluence-exchange/classic-frontend/main/config/main.json"


def get_confluencedex_listings(filepath_or_url=CONFLUENCEDEX_LISTINGS_URL):
    if filepath_or_url.startswith("file://"):
        with open(filepath_or_url) as f:
            return json.load(f)["tokens"]
    else:
        r = requests.get(CONFLUENCEDEX_LISTINGS_URL)
        return r.json()["tokens"]


GET_TOKEN_INFO = "https://etc.blockscout.com/api/tokens/{}"


def get_token_info(addr):
    r = requests.get(
        GET_TOKEN_INFO.format(addr),
        headers={'User-Agent': REQUESTS_USERAGENT})
    return r.json()


BLOCKSCOUT_TOKEN_URL = "https://etc.blockscout.com/api/tokens/{}"


def get_blockscout_token_page(addr):
    r = requests.get(
        BLOCKSCOUT_TOKEN_URL.format(addr),
        headers={'User-Agent': REQUESTS_USERAGENT})
    return r.text


def get_blockscout_contact_info(addr, html_doc=None):
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_blockscout_token_page(addr)
    soup = BeautifulSoup(html_doc, 'html.parser')

    links = soup.find(
        id="ContentPlaceHolder1_tr_officialsite_2").select("ul li a")
    make_link_pair = lambda a: (a["data-original-title"].split(':')[0], a["href"])
    return list(map(make_link_pair, links))


def get_blockscout_notice(addr, html_doc=None):
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_blockscout_token_page(addr)

    soup = BeautifulSoup(html_doc, 'html.parser')
    alert_element = soup.select(
        "body > div.wrapper > div > div.alert.alert-warning")
    if alert_element:
        alert_element = alert_element[0]
        button = alert_element.find("button")
        button.extract()
        return alert_element.decode_contents(formatter="html")
    return None


CMC_ETCDB_URL = "https://confluence-exchange.github.io/coinmarketcap-etctoken-db/tokens/bundle.json"


def get_cmc_etcdb_entry(addr):
    matching_addr_predicate = lambda e: e["address"].lower() == addr.lower()
    etcdb = requests.get(CMC_ETCDB_URL).json()
    return next(filter(matching_addr_predicate, etcdb), None)


CONFLUENCEDEX_GUIDE_URL = "https://rawgit.com/confluence-exchange/confluence-exchange.github.io/main/tokenGuides/{}.ejs"


def get_confluencedex_guide(symbol):
    import requests
    r = requests.get(CONFLUENCEDEX_GUIDE_URL.format(symbol))
    return r.text


def get_cd_token_website(guide_contents):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(guide_contents, 'html.parser')
    footer_link = next(iter(soup.select("blockquote footer a")), None)
    if footer_link:
        return footer_link.attrs["href"]
    return None


def get_cd_token_description(guide_contents):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(guide_contents, 'html.parser')
    content_extractor = lambda paragraph: paragraph.decode_contents(formatter="html")
    guide_description = list(
        map(content_extractor, soup.select("blockquote p")))
    if guide_description:
        return "\n".join(guide_description)
    return None


def get_website(url, render=False):
    import asyncio
    import cfscrape
    from requests_html import HTMLSession

    session = HTMLSession(mock_browser=True)
    requests_ua = session.headers['User-Agent']
    cf_scraper = cfscrape.create_scraper()

    # Run a simple fetch
    response = session.get(url)
    if False and cf_scraper.is_cloudflare_challenge(response):
        # Re-fetch using cfscrape
        try:
            tokens, _ = cfscrape.get_tokens(url, user_agent=requests_ua)
        except ValueError:
            # Presumably occurs when the website does not have cloudflare enabled
            pass
        else:
            response = session.get(url, cookies=tokens)

    if False and render:
        response.html.render(sleep=8)
        return response.html.html
    else:
        return response.html.html


def get_website_metas(url, html_doc=None):
    from bs4 import BeautifulSoup

    if not html_doc:
        html_doc = get_website(url)

    soup = BeautifulSoup(html_doc, 'html.parser')
    meta_tags = soup.find_all('meta')

    metas = []
    for meta in meta_tags:
        if "name" in meta.attrs and meta.attrs["name"] == "description":
            if meta.attrs["content"].strip():
                metas.append((meta.attrs["name"], meta.attrs["content"]))
        elif "property" in meta.attrs and meta.attrs["property"].startswith(
                "og:"):
            if meta.attrs["content"].strip():
                metas.append((meta.attrs["property"], meta.attrs["content"]))
    return metas


def get_website_links(url, html_doc=None):
    from website_links import get_links

    if not html_doc:
        html_doc = get_website(url)

    return get_links(url, html_doc)


def get_canonical_url(from_url):
    import cfscrape
    from bs4 import BeautifulSoup
    import logging

    try:
        r = cfscrape.create_scraper().get(
            from_url, headers={'User-Agent': REQUESTS_USERAGENT})
    except:
        logging.exception("Error while trying to fetch '%s'", url)
        return None

    if (r.headers.get('content-type') or "").startswith('application/'):
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    meta_node = soup.find("link", rel="canonical")
    return meta_node.get("href") if meta_node else None
