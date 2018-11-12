#coding:utf8
import requests
import json
import time
import os
import etc
import re
import io
import sys
from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

verified_url = etc.verified_url

def verify_proxy(IP_info):
    proxies = {
        IP_info['ptype']: IP_info['ptype']+'://' + IP_info['IP'] + ':' + IP_info['port']
    }
    try:
        requests.get(verified_url, proxies=proxies, timeout=10)
    except Exception as e:
        print(e)
        return False, None
    else:
        return True, int(time.time())


'''
check an IP info is a new valuable proxy
if it`s a new valuable one
    insert it to the inactive queue,return Ture
else
    pass,return False

'''
# dcap = dict(DesiredCapabilities.PHANTOMJS)
# dcap["phantomjs.page.settings.userAgent"] = (
# "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36"
# )
# phantomjs_path = r"C:\Users\user\conf\phantomjs-2.1.1-windows\bin\phantomjs.exe"
#
#
# # sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')         #改变标准输出的默认编码
# def get_the_proxy_list():
#     with open('proxy1.json','r')as f:
#         proxy_list = json.load(f)
#     return proxy_list
# def check_proxy_IP(req):
#     pat = re.compile('本机IP:.*?(d+\.d+\.d+\.d+)')
# def test_proxy():
#     proxy_list = get_the_proxy_list()
#     for proxy in proxy_list:
#         proxy = {
#             'http':proxy['IP']+':'+proxy['port']
#         }
#         print (proxy)
#         req = requests.get(test_url,proxies=proxy)
#         check_proxy_IP(req)
# # test_proxy()
# def save_source():
#     proxy_list = get_the_proxy_list()
#     for proxy in proxy_list:
#         proxies = {
#             'http':'http://'+proxy['IP']+':'+proxy['port']
#         }
#         print (proxies)
#         try:
#             service_args = [
#                 '--proxy=%s' % proxies['http'],  # 代理 IP：prot    （eg：192.168.0.28:808）
#                 '--ssl-protocol=any',           #忽略ssl协议
#                 '--load - images = no',         # 关闭图片加载（可选）
#                 '--disk-cache=yes',             # 开启缓存（可选）
#                 '--ignore-ssl-errors=true'     # 忽略https错误(可选)
#             ]
#             print ("it wanner to get a rul")
#             driver = webdriver.PhantomJS(executable_path=phantomjs_path,desired_capabilities=dcap)#,service_args=service_args)
#             driver.get(test_url)
#             print ("it has get the url")
#             # req = requests.get(test_url,proxies=proxies)
#             with open('test{}.html'.format(proxy['IP']),'w',encoding='utf-8')as f:
#                 f.write(driver.page_source)
#             driver.close()
#         except Exception as e:
#             print (e)
#             print('the proxy is error{}'.format(proxy['IP']))
#             pass
#         else:
#             print ('the proxy could be use {}'.format(proxy['IP']))
# save_source()
# req = requests.get(test_url)
# # with open('test.html','w')as f:
# #     f.write(req.text)
# print (req.text)
