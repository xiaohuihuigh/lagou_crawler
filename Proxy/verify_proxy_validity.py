#coding:utf8
import requests
import json
import time
import os
import etc
import re
import io
from lxml import etree
import sys
import proxy_io
verified_url = etc.verified_url
def verify_proxy(IP_info,test_url = etc.test_url):
    proxy = IP_info
    proxies = {
        'http': 'http://' + proxy['IP'] + ':' + proxy['port']
    }
    print(proxy)
    # print (proxies)
    try:
        print("it wanner to get a url")
        rsp = requests.get(url=test_url, proxies=proxies, timeout=10)

        print("it has get the url", etc.test_url)
        print(check_proxy_IP(rsp.text))

    except Exception as e:
        print(e)
        print('the proxy is error{}'.format(proxy['IP']))
        return False,None
    else:
        print('the proxy could be use {}'.format(proxy['IP']))
        return True,int(time.time())

def check_proxy_IP(req):
    word = re.findall(r'<span class="c-gap-right">(.*?)</span>',req)
    return word

def save_source():
    # proxy_list = get_the_proxy_list()
    get_proxies_db = proxy_io.ProxiesIO(db=etc.crawl_db)
    proxy = 1
    put_proxies_db = proxy_io.ProxiesIO(db=etc.alternate_db)
    while proxy:
        proxy = get_proxies_db.pop_proxy()
        proxies = {
            'http':'http://'+proxy['IP']+':'+proxy['port']
        }
        print(proxy)
        # print (proxies)
        try:
            print ("it wanner to get a url")
            rsp = requests.get(url = etc.test_url,proxies=proxies,timeout=10)

            print ("it has get the url",etc.test_url)
            print (check_proxy_IP(rsp.text))

        except Exception as e:
            print (e)
            print('the proxy is error{}'.format(proxy['IP']))
            pass
        else:
            print ('the proxy could be use {}'.format(proxy['IP']))
            put_proxies_db.insert_proxy(proxy)

save_source()