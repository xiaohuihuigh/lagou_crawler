import redisconnector
import etc
host = etc.redis_host
db = etc.redis_db
password = etc.redis_psw
print (host,db,password)
redis_h = redisconnector.RedisConnector(host=host,db=db,password=password)
redis_h.lpush()
# redis_h  =RedisConnector(host='192.168.0.201',db=15,password='linlu')
# ssql ='select distinct task_url from tasks where collect =0'
#
# redis_h.lpush('task',*task_url)
# session_selenium = Session.create_session(driver='/Users/sn0wfree/Documents/lagou/chromedriver_mac',
#                                           sessiontype='Chrome',
#                                           headless=False)
# page_source, session = Lagoul1SourceJson.get_session_selenium_and_page_source(session, url)
# json_type_info, requests_session = Lagoul1SourceJson.get_data_from_json(url,
#                                                                         headers,
#                                                                         pn='1',
#                                                                         session=Session.create_session_requests())
# totalpage = '1'
# L1SJ = Lagoul1SourceJson(session_selenium=session_selenium, headers=headers)
# url, page_source, json_subjobs_dict = L1SJ.GET_POST(url, totalpage)
# # json_type_info2 = json.loads(json_type_info)
#
# result = {'url': url, 'page_source': page_source, 'json_subjobs_dict': json.dumps(json_subjobs_dict),
#           'totalpage': totalpage}
# rS = resultSender()
# rS.set(url, )
# create_task(taskTupleName='lagou_suburl_tasks')
