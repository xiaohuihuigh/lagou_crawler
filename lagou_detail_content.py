# coding=utf8
import copy
import json
import sqlite3
import os, random
# import urlparse
import urllib.parse as urlparse
# from urllib.parse import unquote
import urllib
import redis, logging
import requests
from selenium import webdriver
import pandas as pd
import pymysql
import sqlalchemy
import time
from functools import wraps
import json
import sys

# reload(sys)
# sys.setdefaultencoding('utf8')


# -----retry parameter area start
_tries_ = 10
_delay_ = 5
_backoff_ = 5
server = True


# -----retry parameter area end

# Exception definition area-------

class SpiderExcepetion(Exception):
    pass


class RequireLoginError(SpiderExcepetion):
    def __init__(self, message='Page requires Lgoin process!'):
        super(RequireLoginError, self).__init__(message)  # Q 有什么作用
        self.message = message


class JsonStatusError(SpiderExcepetion):
    def __init__(self, message='Status is False!'):
        super(JsonStatusError, self).__init__(message)
        self.message = message


class NoJobsError(SpiderExcepetion):
    def __init__(self, message='No Jobs in the Page!'):
        super(NoJobsError, self).__init__(message)
        self.message = message


# Exception definition area-end------

# Dark Magic area-----------
def retry(exception_to_check, tries=10, delay=2, backoff=1, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param exception_to_check: the exception to check. may be a tuple of
        exceptions to check
    :type exception_to_check: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except exception_to_check as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


# Dark Magic area-----------


# DB controller area -------


class RedisConnector(redis.Redis):
    def __init__(self, host='192.168.0.201', port=6379, password='linlu', db=0):
        # self.redis = redis.Redis.from_url('redis://{}@{}:{}/{}'.format(password, host, port, db))
        super(RedisConnector, self).__init__(host=host, port=port, password=password, db=db)
        # self.r = redis.Redis()

    @staticmethod
    def byte2str(b):
        return b.decode('utf8') if isinstance(b, bytes) else b

    def create_list(self, listname, *values):
        self.lpush(listname, *values)

    def add_value_into_list(self, listname, *values):
        self.lpush(listname, *values)

    def obtain_a_task_once(self, redis_key, *para):
        return self.lpop(redis_key)

    def obtain_a_task_else_waiting(self, redis_key, timeout=10):
        return self.blpop(redis_key, timeout)


'''
链接mysql数据库
参数为
    host = '192.168.0.206'
    port = 3306
    user = 'crawler'
    psw = 'crawler'
    charset = 'UTF8'
    dbname = 'alternative'
'''


class ConnectMysql(object):
    # C_RR_ResearchReport
    def __init__(self, MysqlName, host='192.168.0.206', port=3306, user='crawler', passwd='crawler', charset='UTF8',
                 db='test_alternative'):
        # super(LRUDict_UnPickled, self).__init__()
        from collections import namedtuple
        SQLConnector = namedtuple(MysqlName, ['host', 'port', 'user', 'passwd', 'charset', 'db'])
        self.para = SQLConnector(host, port, user, passwd, charset, db)

    def sql2data(self, sql):
        """
        直接传入sql语句，进行运行
        :param sql:
        :return:
        """

        conn = self.SelfConnect()
        df = pd.read_sql(sql, conn)
        conn.close()
        return df

    def DetectConnectStatus(self, returnresult=True, printout=False):
        """

        :param returnresult:
        :param printout:
        :return:
        """
        try:
            result = self.Excutesql()
            status = 'Good connection!'
            if printout:
                print(status)
        except pymysql.OperationalError as e:
            result = str(e)
            status = 'Bad connection!'
            if printout:
                print(e)
        finally:
            if returnresult:
                return result
            else:
                return status

    def SelfConnect(self):
        """

        :return:
        """
        conn = pymysql.connect(host=self.para.host, port=self.para.port, user=self.para.user, passwd=self.para.passwd,
                               charset=self.para.charset, db=self.para.db)
        return conn

    def SelfEngine(self):
        """

        :return:
        """
        engine = sqlalchemy.create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}?charset={}'.format(self.para.user, self.para.passwd, self.para.host,
                                                               self.para.port, self.para.db,
                                                               self.para.charset))  # 用sqlalchemy创建引擎
        # print(engine)
        return engine

    '''
    所以engine是干嘛的？？？
    '''

    def DF2mysql(self, df, tablename, engine='SelfEngine', if_exists='append', index=False):
        if isinstance(engine, str) and engine == 'SelfEngine':
            df.to_sql(tablename, con=self.SelfEngine(), if_exists=if_exists, index=index)
        else:
            df.to_sql(tablename, con=engine, if_exists=if_exists, index=index)

    def Excutesql(self, sql='SHOW DATABASES'):
        conn = self.SelfConnect()
        cur = conn.cursor()
        cur.execute(sql)  # 执行该语句
        result = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return result

    def SHOWDATABASES(self):
        return self.Excutesql()

    def SHOWTABLES(self):
        return self.Excutesql(sql='SHOW TABLES')

    def byte2str(b):
        return b.decode('utf8') if isinstance(b, bytes) else b


# DB controller area -------


class Session(object):
    @classmethod
    def create_session(cls,
                       driver,
                       sessiontype='Chrome',
                       headless=True,
                       implicitlywait=10,
                       Force=False):
        if sessiontype == 'PhantomJS':
            return cls.create_session_PhantomJS(driver=driver,
                                                headless=headless,
                                                implicitlywait=implicitlywait,
                                                Force=Force)
        elif sessiontype == 'Chrome':
            return cls.create_session_Chrome(driver=driver,
                                             headless=headless,
                                             implicitlywait=implicitlywait,
                                             Force=Force)
        elif sessiontype == 'Requests':
            return requests.session()
        else:
            raise ValueError('unknown session arguments:{}. Please Check!'.format(sessiontype))

    @staticmethod
    def create_session_PhantomJS(driver,
                                 headless=True,
                                 implicitlywait=10,
                                 Force=False):
        print("Phantom", driver)
        os.environ["webdriver.phantomjs.driver"] = driver
        print(os.environ["webdriver.phantomjs.driver"])

        session = webdriver.PhantomJS(driver)
        session.implicitly_wait(implicitlywait)

        return session

    @staticmethod
    def create_session_requests():
        return requests.session()

    @staticmethod
    def create_session_Chrome(driver='/Users/sn0wfree/Documents/lagou/chromedriver_mac',
                              headless=True,
                              implicitlywait=10,
                              Force=False):

        # driver = self.chooseDriver(Force, backend)

        os.environ["webdriver.chrome.driver"] = driver
        if headless:
            # driver = 'chromedriver_linux'

            # Create augments object for Chrome
            opt = webdriver.ChromeOptions()
            # turn Chrome into headless model no matter in windows or linux, it is autofit for everything
            # opt.set_headless()
            opt.add_argument('--headless')
            opt.add_argument(
                '--no-sandbox')  # required when running as root user. otherwise you would get no sandbox errors.
            # set up Chrome headless object
            session = webdriver.Chrome(driver, options=opt)
        else:
            session = webdriver.Chrome(driver)

        # chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument(
        #     '--no-sandbox')  # required when running as root user. otherwise you would get no sandbox errors.
        # session = webdriver.Chrome(chrome_path, chrome_options=chrome_options)
        session.implicitly_wait(implicitlywait)
        return session


class Lagoul1SourceJson(object):
    def __init__(self,
                 session_selenium,
                 session_requests=None,
                 headers=None):
        session_selenium, session_requests = self.session_init_(session_selenium, session_requests)
        self.session_selenium = session_selenium
        self.session_requests = session_requests
        self.default_headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'} if headers is None else headers
        # self.headers = self.deflaut_headers

    def GET_POST(self, url, totalpage, headers=None, Content_Type='application/x-www-form-urlencoded', sleep=5):
        """
        get request and post request in one function !
        :param url:
        :param totalpage:
        :param headers:
        :return:
        """
        if headers is None:
            headers = copy.deepcopy(self.default_headers)
            headers['Content-Type'] = Content_Type
        else:
            # headers = headers
            pass

        page_source, session_ = self.get_session_selenium_and_page_source(self.session_selenium, url)
        json_subjobs_dict = {}
        try:
            if str(totalpage) == '0':
                logging.warning('no jobs in the pages')
                return url, page_source, None
            else:
                requests_session = self.session_requests

                for page_num in range(int(totalpage)):
                    real_page = page_num + 1
                    print(real_page)
                    s_req_text, requests_session = self.get_data_from_json(url,
                                                                           headers=headers,
                                                                           pn=str(real_page),
                                                                           session=requests_session)
                    json_subjobs_dict[str(real_page)] = s_req_text
                    time.sleep(sleep * (1 + random.random()))
                return url, page_source, json_subjobs_dict
        except (RequireLoginError, JsonStatusError, NoJobsError) as e:
            print(e)
            return url, e, None
        except Exception as e:
            print(e)
            return url, e, None

    @classmethod
    def session_init_(cls, session_selenium, session_requests=None):
        """
        init session for some collection
        :param session_selenium:
        :param session_requests:
        :return:
        """

        session_requests = Session.create_session_requests() if session_requests is None else session_requests
        return session_selenium, session_requests

    @staticmethod
    @retry(exception_to_check=JsonStatusError, tries=_tries_, delay=_delay_, backoff=_backoff_, logger=None)
    def get_data_from_json(url,
                           headers,
                           session=requests.session(),
                           url_json_base='https://www.lagou.com/jobs/positionAjax.json?', pn='1'):
        """
        sub-core for the parse the json data from the api or the post request
        :param url:
        :param headers:
        :param session:
        :param url_json_base:
        :param pn:
        :return:
        """
        # pa_auto = dict((urllib.parse.unquote(p).split('=') for p in url.rstrip('#filterBox').split(url_json_base)[-1].split("&")))
        pa_auto = dict(
            (urlparse.unquote(p).split('=') for p in url.rstrip('#filterBox').split(url_json_base)[-1].split("&")))
        pa_auto.update({'needAddtionalResult': 'false'})

        pa_auto.update({'pn': pn})
        Referer = "{}".format(url.rstrip('#filterBox'))
        headers['Referer'] = Referer

        # px: default
        # city: 南京
        # needAddtionalResult: false

        s_req = session.post(url_json_base, data=pa_auto, headers=headers)
        json_type_info = json.loads(str(s_req.text))
        if isinstance(json_type_info['success'], bool) and json_type_info['success']:
            return str(s_req.text), session
            # raise JsonStatusError('Json Status Failure!')
        else:
            raise JsonStatusError('Json Status Failure!')

    @staticmethod
    @retry(exception_to_check=RequireLoginError, tries=_tries_, delay=_delay_, backoff=_backoff_, logger=None)
    def get_session_selenium_and_page_source(session, url):
        """
        sub-core for the parse the page source
        :param session:
        :param url:
        :return:
        """
        session.get(url)
        page_source = session.page_source
        url_d = session.current_url
        if url_d.startswith('https://passport.lagou.com/'):
            RequireLoginError('require login!')
            # raise ValueError('require login!')
        else:

            print('url normal:{}'.format(url))
        return page_source, session


class MresultSender(ConnectMysql):
    def __init__(self, host='192.168.0.206', port=3306, user='crawler', passwd='crawler', charset='UTF8',
                 db='test_alternative'):
        super(MresultSender, self).__init__(MysqlName='mysql', host=host, port=port, user=user, passwd=passwd,
                                            charset=charset, db=db)

    def send(self, result):
        print('result', result)
        result = json.loads(result)["result"]
        url = str(result["url"])
        page_source = str(result["page_source"]).replace('"', '“')
        json_subjobs_dict = str(result["json_subjobs_dict"]).replace('"', '“')
        totalpage = int(result["totalpage"])
        cmd_update_result = """insert into textlagou_result(task_url,page_source,json_subjobs_dict,totalpage)
        values("%s","%s","%s","%d")""" % (url, page_source, json_subjobs_dict, totalpage)
        self.Excutesql(cmd_update_result)
        print("send success")


class MtaskGeter(ConnectMysql):
    def __init__(self, host='192.168.0.206', port=3306, user='crawler', passwd='crawler', charset='UTF8',
                 db='test_alternative'):
        super(MtaskGeter, self).__init__(MysqlName='mysql', host=host, port=port, user=user, passwd=passwd,
                                         charset=charset, db=db)

    '''
    没用吧
    '''

    def getTask(self, timeout=100, jsoned=True):
        TTN, task = self.get_a_task(timeout=timeout)
        print(TTN, task)
        return task

    def get_a_task(self, timeout=3):
        cmd_get_a_task = "SELECT * FROM tasks WHERE collect != 1 AND TotalNum != 0 LIMIT 1"
        conn = self.SelfConnect()
        cur = conn.cursor()
        TNN = cur.execute(cmd_get_a_task)  # 执行该语句
        result = cur.fetchone()
        '''
        进行任务的标记
        '''
        cmd_update_the_task = "UPDATE tasks SET collect =1 WHERE task_url='{}' AND TotalNum = '{}' ".format(result[1],
                                                                                                            result[2])

        cur.execute(cmd_update_the_task)
        conn.commit()
        cur.close()
        conn.close()
        return TNN, result


class taskGeter(RedisConnector):
    def __init__(self, host='120.78.81.81', port=6379, password='eef1ef8031e75ca1849c6a590f10ccb0', db=1):
        super(taskGeter, self).__init__(host=host, port=port, password=password, db=db)

    def get_current_queue_length(self, taskTupleName):
        return self.llen(taskTupleName)

    def getTask(self, taskTupleName, timeout=100, jsoned=True):
        TTN, task = self.obtain_a_task_else_waiting(taskTupleName, timeout=timeout)

        if jsoned and task is not None:
            task2 = self.byte2str(task)
            clean_task = json.loads(task2)
            return clean_task
        else:
            return task


class resultSender(RedisConnector):
    def __init__(self, host='120.78.81.81', port=6379, password='eef1ef8031e75ca1849c6a590f10ccb0', db=2):
        super(resultSender, self).__init__(host=host, port=port, password=password, db=db)

    def send(self, key, result):
        # print 'result',result
        dumped_result = json.dumps(result)
        self.set(key, dumped_result)


def create_task(taskTupleName, lagou='job_lagou.sqlite', task_db=1, ):
    redis = RedisConnector(db=task_db)
    with sqlite3.connect(lagou) as conn:
        url_num = pd.read_sql('select ChildUrl_level1,TotalNum from lagou where TotalNum > 0 ', conn)
        tasks = url_num.values.tolist()
        jsoned_tasks = [json.dumps(task) for task in tasks]
        redis.lpush(taskTupleName, *jsoned_tasks)


def detectplatform(browser='Chrome', server=server):
    import platform
    system_info = platform.system()
    if system_info == 'Darwin':
        if browser == 'Chrome':
            return '/Users/sn0wfree/Documents/lagou/chromedriver_mac'
        elif browser == 'PhantomJs':
            return '/Users/sn0wfree/Documents/lagou/phantomjsdriver_mac'
    elif system_info == 'Windows':
        if browser == 'Chrome':
            return '/Users/user/conf/chromedriver.exe'
        elif browser == 'PhantomJs':
            # return '/User/user/conf/phantomjs.exe'
            return r"C:\Users\user\conf\phantomjs-2.1.1-windows\bin\phantomjs.exe"
    else:
        return '/home/{}/Downloads/phantomjs-2.1.1-linux-x86_64/bin/phantomjs'.format("linlu" if server else "snowfree")

        # return '/home/zhaoyinghui/conf/phantomjs/bin/phantomjs'


def run_task(driver=detectplatform(),
             headers=None):
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Encoding': 'gzip, deflate, br',
               'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'} if headers is None else headers
    # init redis connector
    # tG = taskGeter(db=task_db)
    tG = MtaskGeter()
    # rS = resultSender(db=save_db)
    rS = MresultSender()
    session_selenium = Session.create_session(driver=driver,
                                              sessiontype='PhantomJS',
                                              headless=True)

    L1SJ = Lagoul1SourceJson(session_selenium=session_selenium, headers=headers)

    # length = tG.get_current_queue_length(taskTupleName)

    while 1:
        # get task
        task = tG.getTask()
        if task is None:
            break

        index, url, totalpage, collect = task
        url, page_source, json_subjobs_dict = L1SJ.GET_POST(url, totalpage)
        # print url
        # print page_source
        # print json_subjobs_dict
        try:
            result = {'url': url,
                      'page_source': page_source,
                      'json_subjobs_dict': json.dumps(json_subjobs_dict) if json_subjobs_dict is not None else None,
                      'totalpage': totalpage}
            dumped_result = json.dumps({'result': result})
            # send result
            if json_subjobs_dict is not None:
                rS.send(dumped_result)
        except Exception as e:
            raise e

        # task = tG.getTask(taskTupleName)
    print('tasks completed!')


if __name__ == '__main__':
    page_info_dict = {'totalNum': '//*[@id="order"]/li/*/div[@class="page-number"]/span[2]',
                      'curNum': '//*[@id="order"]/li/*/div[@class="page-number"]/span[1]'}
    url = "https://www.lagou.com/jobs/list_HTML5?px=default&city=%E5%8E%A6%E9%97%A8#filterBox"
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Encoding': 'gzip, deflate, br',
               'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
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

    # tG = taskGeter(db=1)
    run_task(driver=detectplatform("PhantomJs"))
