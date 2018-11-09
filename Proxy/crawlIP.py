import requests
from bs4 import BeautifulSoup as bf
import time
import json
inha_url = 'http://www.kuaidaili.com/free/inha/{}/'
intr_url = 'www.kuaidaili.com/free/intr/{}/'
def get_html_to_soup(url):
    print(url)
    response = requests.get(url)
    soup = bf(response.text,'html.parser')
    return soup

def get_proxys_info(soup):
    proxys_info_list = []
    proxy_soup_list = soup.select('tbody > tr')
    # print(proxys_soup)

    for proxy_soup in proxy_soup_list:
        proxy_info_dict = {}
        proxy_info_list = proxy_soup.findAll('td')
        info_list = ['IP','port','anonymity','ptype','locate','resspeed','last_c_time']
        for i in range(len(info_list)):
            proxy_info_dict[info_list[i]] = proxy_info_list[i].text
        proxys_info_list.append(proxy_info_dict)
    return proxys_info_list
for i in range(1,6):
    time.sleep(3)
    soup = get_html_to_soup(inha_url.format(i))
    proxys_list = get_proxys_info(soup)
    # print (proxys_list)
    # print (json.dumps(proxys_list))

    with open('proxy{}.json'.format(i),'w')as f:
        # json.dumps(proxys_list)
        json.dump(proxys_list,f)
