import requests
from bs4 import BeautifulSoup as bf
import time
import json
import etc
import proxy_io
def get_html_to_soup(url):
    print(url)
    response = requests.get(url)
    soup = bf(response.text,'html.parser')
    return soup

def get_proxies_info(soup):
    proxies_info_list = []
    proxy_soup_list = soup.select('tbody > tr')

    for proxy_soup in proxy_soup_list:
        proxy_info_dict = {}
        proxy_info_list = proxy_soup.findAll('td')
        info_list = ['IP','port','anonymity','ptype','locate','resspeed']
        for i in range(len(info_list)):
            proxy_info_dict[info_list[i]] = proxy_info_list[i].text
        proxies_info_list.append(proxy_info_dict)
    return proxies_info_list
def crawl_proxies():
    for i in range(1,50):
        time.sleep(3)
        soup = get_html_to_soup(etc.inha_url.format(i))
        proxies_list = get_proxies_info(soup)
        proxy_db = proxy_io.ProxiesIO(db = etc.crawl_db)
        for proxy in proxies_list:
            proxy_db.insert_proxy(proxy)
crawl_proxies()