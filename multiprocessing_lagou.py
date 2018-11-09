# coding=utf8
import json
import random
import time

from multiprocessing import Pool
from threading import Lock

import pandas as pd
import pymysql

import logging
import logging.handlers

# extension --------------------

from redisconnector import RedisConnector
from Uniqueness import Uniqueness

import lagou_detail_content

# -------------- parameter area
get_task_lock = Lock()
put_result_lock = Lock()

com_paras = {'host': '192.168.0.201', 'port': 6379, 'password': 'linlu', 'db': 13}

# -----reload retry parameter area start

lagou_detail_content._tries_ = 20
lagou_detail_content._delay_ = 3
lagou_detail_content._backoff_ = 3
lagou_detail_content.server = True
# -----retry parameter area end

# core ------ start

from lagou_detail_content import detectplatform, Session, Lagoul1SourceJson, MtaskGeter

# core -------- end


# extension --------------------

global _count_
_count_ = 1


# -----

class Logger(object):
    def __init__(self,
                 LOG_FILE='lagou.log',
                 PyName='lagou_alternative',
                 fmt='%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'):
        handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)  # 实例化handler
        console_handler = logging.StreamHandler()  # 屏幕输出

        # console_handler.setFormatter('%(name)-12s: %(levelname)-8s %(message)s')

        formatter = logging.Formatter(fmt)  # 实例化formatter
        handler.setFormatter(formatter)  # 为handler添加formatter

        self.logger = logging.getLogger(PyName)  # 获取名为tst的logger
        self.logger.addHandler(handler)  # 为logger添加handler
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

    def test(self):
        self.INFO('first info message')
        self.DEBUG('first debug message')

    def INFO(self, txt):
        self.logger.info(txt)

    def DEBUG(self, txt):
        self.logger.debug(txt)


logger_sys = Logger(LOG_FILE='lagou.log')


def run_task(driver=detectplatform(), headers=None):
    # length = tG.get_current_queue_length(taskTupleName)
    pool = Pool(processes=5)
    while 1:
        # print 'front the pool apply'
        # print 1

        pool.apply_async(get_result, args=(driver, headers))
        time.sleep(5)
        # pool.apply(func=Foo,args=(3,))
        # print "after the pool apply"
        # get task
    pool.close()
    pool.join()


def L_getTask(tG):
    global get_task_lock
    get_task_lock.acquire()
    ans = tG.getTask()
    print('get the task')
    get_task_lock.release()
    return ans


def redis_getTask(rlist_name, com_paras, timeout=100):
    com_paras['db'] = 13  # use 13 database
    r = RedisConnector(**com_paras)
    ret = r.obtain_a_task_else_waiting(rlist_name, timeout=timeout)
    return r.byte2str(ret[1])


def L_send(result, rS):
    global put_result_lock
    put_result_lock.acquire()
    ans = rS.send(result)
    put_result_lock.release()
    return ans


class LagouProcessComponent(object):

    @staticmethod
    def get_tasks_via_multi_src(task, tG, source, rlist_name, com_para, timeout):
        if source == 'Mysql':
            task = L_getTask(tG) if task is None else task
        else:
            task = redis_getTask(rlist_name, com_para, timeout=timeout) if task is None else task
        return task

    @staticmethod
    def first_check_set_collect_1_to_mark(sql_update_1st_check, tG, logger_sys):
        # set collect as 1 to mark
        logger_sys.INFO('[SQL][Mask Task]: {} '.format(sql_update_1st_check))
        tG.Excutesql(sql_update_1st_check)  # first check

    @staticmethod
    def parse_spider_data(url, totalpage, page_source, json_subjobs_dict, logger_sys):
        logger_sys.INFO('[Spider][Save Data]: preparing to store data on {} '.format(url))
        escape_string = pymysql.escape_string
        result = {'uuid_url': str(Uniqueness.generateUUID(url)),
                  'task_url': url,
                  'page_source': escape_string(page_source),
                  'json_subjobs_dict': escape_string(
                      json.dumps(json_subjobs_dict)) if json_subjobs_dict is not None else None,
                  'totalpage': totalpage}
        return result

    @staticmethod
    def insert_spider_data(tgb_result, table_result, tG, logger_sys):
        col = ','.join(tgb_result.columns)
        a = ['("' + '","'.join(map(str, row)) + '")' for row in tgb_result.values.tolist()]
        sql_insert_data = 'INSERT IGNORE INTO {}({}) VALUES {}'.format(table_result, col, ','.join(a))
        logger_sys.INFO('[SQL][Mask Task]: {} '.format(sql_insert_data[:100]))
        # --------------
        tG.Excutesql(sql_insert_data)  # insert data

    @staticmethod
    def second_check_set_done_as_1_to_mark(task_table, url, tG, logger_sys):
        # -------------------
        # SET Done as 1 to mark tasks finished
        sql_update_2nd_check = 'UPDATE {} SET Done = 1 WHERE task_url = "{}"'.format(task_table, url)
        logger_sys.INFO('[SQL][Check Task]:  {} '.format(sql_update_2nd_check))
        tG.Excutesql(sql_update_2nd_check)  # finally task_table check

    @staticmethod
    def print_speed(speed):
        global _count_
        print("required about {} min; left {} tasks".format(_count_ * speed / 60.0, _count_))


def get_result(task,
               r_list_name='tasks',
               com_para=None,
               timeout=100,
               driver=detectplatform("PhantomJs"),
               headers=None,
               task_table='tasks',
               table_result='textlagou_result', source='Mysql'):
    f = time.time()
    time.sleep(1 + random.random())

    com_para = com_paras if com_para is None else com_para

    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Encoding': 'gzip, deflate, br',
               'Content-Type': 'application/x-www-form-urlencoded',
               'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'} if headers is None else headers
    # parameter area ----------------------------
    # init redis connector

    # obtain task
    tG = MtaskGeter()

    # rS = MresultSender()
    logger_sys.INFO('Obtaining task')

    task = LagouProcessComponent.get_tasks_via_multi_src(task, tG, source, r_list_name, com_para, timeout)

    if task is None:
        return False
    else:
        index, url, total_page, collect, *done = task
        logger_sys.INFO('Task obtained!')
        # active session

        session_selenium = Session.create_session(driver=driver,
                                                  sessiontype='PhantomJS',
                                                  headless=True)

        L1SJ = Lagoul1SourceJson(session_selenium=session_selenium, headers=headers)

        # set collect as 1 to mark
        sql_update_1st_check = 'UPDATE {} SET collect = 1 WHERE task_url = "{}"'.format(task_table, url)

        LagouProcessComponent.first_check_set_collect_1_to_mark(sql_update_1st_check, tG, logger_sys)
        # ---------
        # process
        logger_sys.INFO('[Spider][Process Task]: process url: {} '.format(url))

        url, page_source, json_subjobs_dict = L1SJ.GET_POST(url, total_page)

        # preparing to store data
        result = LagouProcessComponent.parse_spider_data(url, total_page, page_source, json_subjobs_dict, logger_sys)

        # send result
        tgb_result = pd.DataFrame(result, index=[1])
        # insert data
        LagouProcessComponent.insert_spider_data(tgb_result, table_result, tG, logger_sys)

        # -------------------
        # finally task_table check
        # SET Done as 1 to mark tasks finished
        LagouProcessComponent.second_check_set_done_as_1_to_mark(task_table, url, tG, logger_sys)

        # L_send(dumped_result, rS)
        time.sleep(lagou_detail_content._delay_ * random.random())

        logger_sys.INFO('[Spider][Check Task]:  {} Done! '.format(url))

        LagouProcessComponent.print_speed(time.time() - f)
        session_selenium.quit()
        return True


if __name__ == "__main__":
    tG = MtaskGeter()
    _count_ = tG.sql2data('SELECT count(task_url) FROM tasks WHERE Done =0 ').values.ravel()[0]  # counter
    print(_count_)
    while 1:
        try:
            if _count_ <= 0:
                break
            get_result(None, driver=detectplatform("PhantomJs"))
            _count_ -= 1
            print(_count_)
            # if _count_ <= 0:
            #    break
        except AttributeError as e:
            print(e)

            pass
    # run_task(driver=detectplatform("PhantomJs"))

    # boost_up(get_result, )
    # print detectplatform('PhantomJs')
    # run_task()

# https://www.lagou.com/jobs/list_Android?px=default&xl=%E6%9C%AC%E7%A7%91&city=%E8%A5%BF%E5%AE%89#filterBox
