# coding=utf8

import redis
import sqlite3
import pandas as pd

com_paras = {'host': '192.168.0.201', 'port': 6379, 'password': 'linlu', 'db': 8}


class RedisConnector(redis.Redis):
    def __init__(self, host='192.168.0.201', port=6379, password='linlu', db=10):
        # self.redis = redis.Redis.from_url('redis://{}@{}:{}/{}'.format(password, host, port, db))
        super(RedisConnector, self).__init__(host=host, port=port, password=password, db=db)
        # self.r = redis.Redis()

    def excute_command(self, commd, *key):
        pass

    def create_list(self, listname, *values):
        self.lpush(listname, *values)

    def add_value_into_list(self, listname, *values):
        self.lpush(listname, *values)

    def obtain_a_task_once(self, redis_key, *para):
        return self.lpop(redis_key)

    def obtain_a_task_else_waiting(self, redis_key, timeout=10):
        return self.blpop(redis_key, timeout)

    @staticmethod
    def byte2str(b):
        return b.decode('utf8') if isinstance(b, bytes) else b


if __name__ == '__main__':
    def load_task(tasktable='lagou_csv_l1', sqlitefile='job_lagou.sqlite'):
        with sqlite3.connect(sqlitefile) as conn:
            tasks_df = pd.read_sql(
                'select parsed_Job_City from {} where Collected = 0  '.format(tasktable),
                conn)
            return tasks_df


    # tasks_df = load_task()
    rr = RedisConnector(**com_paras)
    # rr.create_list('LagouTaskstest', *tasks_df.values.ravel())
    # rr.add_value_into_list('tasks', [1])
    retu = rr.obtain_a_task_else_waiting('tasks', 1)
    print(retu, retu is not None)
    # print(type(retu), type(retu.decode('utf8')))
    print(isinstance(retu, bytes))
