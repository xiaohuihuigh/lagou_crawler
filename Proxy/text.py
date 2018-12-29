import redisconnector
import etc
import redis
import json
import time


# redis_h.lpush()
class ProxiesIO(redis.Redis):
    def __init__(self, host=etc.redis_host, port=etc.redis_port, password=etc.redis_psw, db=etc.redis_db):
        super(ProxiesIO, self).__init__(host=host, port=port, password=password, db=db)
        # 可以在初始化的时候创建如果没有list的话？？？
        # 具体看怎么存的。。。

r = ProxiesIO()
i = 12306
while 1:
    i+=1
    # time.sleep(1)
    r.set(i,i ** i)
    print (i)
    r.expire(i,300)
    if not r.exists('1'):
        break
    # @staticmethod
    # def get_IPkey(IP_info):
    #     IP = IP_info['IP']
    #     port = int(IP_info['port'])
    #     ip_list = IP.split('.')
    #     key = 0
    #     for i in ip_list:
    #         key = key * 1000 + int(i)
    #     _port = port
    #     while _port:
    #         key *= 10
    #         _port //= 10
    #     key += port
    #     return key
    #
    # '''
    # 暂时还不知道是干嘛的。。。
    # '''
    # # def create_list(self, listname, *values):
    # #     self.lpush(listname, *values)
    #
    # '''
    # 检测IP的是否存在于数据库中，存在返回True并返回上次验证的时间，不存在返回False和None
    # '''
    #
    # def check_proxy(self, IP_info):
    #     IPkey = self.get_IPkey(IP_info)
    #     print(IP_info)
    #     print('get an IPkey', IPkey)
    #     if self.exists(IPkey):
    #         IP_info = self.get(IPkey)
    #         IP_info = json.loads(IP_info)
    #         return True, IP_info['last_c_time']
    #     else:
    #         return False, None
    #
    # '''
    # 插入数据成功返回Ture，没有成功插入返回False，暂时没有影响
    # '''
    #
    # def insert_proxy(self, IP_info):
    #     IPkey = self.get_IPkey(IP_info)
    #     try:
    #         self.set(IPkey, json.dumps(IP_info))
    #     except Exception as e:
    #         print('insert the proxy', IP_info, 'false')
    #         return False
    #     else:
    #         return True
    #
    # '''
    # 从数据库中拿到一个可用的IP信息
    # 返回一条json格式的IP信息
    #
    # 采用多线程的等待模式 blpop ，等待时间10s
    # '''
    #
    # def pop_proxy(self):
    #     IPkey = self.randomkey()
    #     IP_info = self.get(IPkey)
    #     self.delete(IPkey)
    #     IP_info = json.loads(IP_info)
    #     return IP_info
    #
    # # '''
    # # 从数据库中拿到n个可用信息
    # # 返回一个列表，列表中的每一个元素为一个json格式的IP信息
    # # '''
    # # def pop_n_proxies(self,n):
    # #     proxies_list = []
    # #     for i in range(n):
    # #         proxies_list.append(self.pop_proxy())
    # #     return proxies_list
    # '''
    # 返回一个列表的长度
    # '''
    #
    # def check_len_db(self):
    #     return self.dbsize()
    #
    # @staticmethod
    # def byte2str(b):
    #     return b.decode('utf8') if isinstance(b, bytes) else b
