import redisconnector
import etc
import redis
# redis_h.lpush()
class ProxiesIO(redis.Redis):
    def __init__(self,host=etc.redis_host,port = etc.redis_port,password=etc.redis_psw,db=etc.redis_db):
        super(ProxiesIO,self).__init__(host=host,port=port,password=password,db=db)
        #可以在初始化的时候创建如果没有list的话？？？
        #具体看怎么存的。。。
    '''
    暂时还不知道是干嘛的。。。
    '''
    def create_list(self, listname, *values):
        self.lpush(listname, *values)


    '''
    检测IP的是否存在于数据库中，存在返回True并返回上次验证的时间，不存在返回False和None
    '''
    def check_proxy(self,IP_info):

        return True,'time' or False,None
    '''
    插入数据成功返回Ture，没有成功插入返回False，暂时没有影响
    '''
    def insert_proxy(self,IP_info):
        return True or False
    '''
    从数据库中拿到一个可用的IP信息
    返回一条json格式的IP信息
    
    采用多线程的等待模式 blpop ，等待时间10s
    '''
    def pop_proxy(self):
        IP_info = 'get a IP'
        return IP_info
    '''
    从数据库中拿到n个可用信息
    返回一个列表，列表中的每一个元素为一个json格式的IP信息
    '''
    def pop_n_proxies(self,n):
        proxies_list = []
        for i in range(n):
            proxies_list.append(self.pop_proxy())
        return proxies_list
    '''
    返回一个列表的长度
    '''
    def check_len_db(self):
        return self.llen()
    @staticmethod
    def byte2str(b):
        return b.decode('utf8') if isinstance(b, bytes) else b

#
# class RedisConnector(redis.Redis):
#     def __init__(self, host='192.168.0.201', port=6379, password='linlu', db=10):
#         # self.redis = redis.Redis.from_url('redis://{}@{}:{}/{}'.format(password, host, port, db))
#         super(RedisConnector, self).__init__(host=host, port=port, password=password, db=db)
#         # self.r = redis.Redis()
#
#     def excute_command(self, commd, *key):
#         pass
#
#
#     def add_value_into_list(self, listname, *values):
#         self.lpush(listname, *values)
#
#     def obtain_a_task_once(self, redis_key, *para):
#         return self.lpop(redis_key)
#
#     def obtain_a_task_else_waiting(self, redis_key, timeout=10):
#         return self.blpop(redis_key, timeout)
#
#     @staticmethod
#     def byte2str(b):
#         return b.decode('utf8') if isinstance(b, bytes) else b