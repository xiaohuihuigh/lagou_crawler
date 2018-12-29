import proxy_io
import verify_proxy_validity
import time
import etc
import json
'''
处理一条IP的流程的类
包含，
    获取一条IP
    将IP入库或丢弃
        在type alternate 中没有from_db to_db 是alternate queue
        在type immediate 中from_db 是alternate queue to_db 是 immediate queue
        在type to_use 中 from_db 和to_db 都是immediate queue
    检测要to_db的长度
'''
class Proxy_processing(object):
    def __init__(self,type,from_db,to_db,effective_time=None,mlen = None):
        if effective_time == None:
            if type == 'alternate':
                effective_time = etc.alternate_effective_time
            elif type == 'immediate':
                effective_time = etc.immediate_effective_time
            elif type == 'to_use':
                effective_time = etc.to_use_effective_time
        if mlen == None:
            if type == 'alternate':
                mlen = etc.alternate_mlen
            elif type == 'immediate':
                mlen = etc.immediate_mlen
        self.from_db=from_db
        self.to_db = to_db
        self.type=type
        self.mlen = mlen
        self.effective_time=effective_time
        self.from_redis = proxy_io.ProxiesIO(db=self.from_db)
        self.to_redis = proxy_io.ProxiesIO(db=self.to_db)
    '''
    ##未完 alternate的get_a_proxy还没有写
    
    从from_db或其他途径得到一个proxy，如果获得成功返回成功，没有得到就再运行一次并输出错误
    '''
    def get_a_proxy(self):
        if self.type == 'alternate':
            IP_info = alternate_get_a_proxy()
            print(IP_info)
            if IP_info == None:
                return False,None
            return True,IP_info
            # return False,None
        elif self.type == 'immediate':
            try:
                IP_info=self.from_redis.pop_proxy()
            except Exception as e:
                print (e)
                return self.get_a_proxy()
            return True,IP_info
    '''
    获得一个IP，在检测可用性后如果可用加入to_db中，不可用raise一个错误出来
    '''
    def push_or_discare(self,IP_info):
        intf,last_c_time=self.to_redis.check_proxy(IP_info)
        print('intf',intf,'lastctime',last_c_time)
        if (intf and int(time.time()) - last_c_time >=self.effective_time) or not intf:#在队列中但是超过有效时间
            fn,last_c_time=verify_proxy_validity.verify_proxy(IP_info)
            if fn == True:
                IP_info['last_c_time'] = last_c_time
                self.to_redis.insert_proxy(IP_info)
            else:

                raise ValueError('a no useful proxy',IP_info['IP'])
        else:
            print('the proxy is in the {} queue'.format(self.type))
    '''
    检测to_db中的数据是否到达要加入的最小临界点
    '''
    def should_add_to_db(self):
        return self.to_redis.check_len_db() - self.mlen < 0

def alternate_get_a_proxy():
    for i in range(20,25):
        path = 'proxy'+str(i)+'.json'
        with open(path,'r')as f:
            dict_list = json.load(f)
        if len(dict_list) == 0:
            continue
        else:
            IP_info = dict_list[0]
            dict_list = dict_list[1:]
            with open(path,'w') as f:
                json.dump(dict_list,f)
            print('alternate_get_a_proxy',IP_info)
            return IP_info
    return None


def alternate_process():
    ap = Proxy_processing(type='alternate',from_db=None,to_db=etc.alternate_db)
    while 1:
        if ap.should_add_to_db():

            print('test alternate')
            for i in range(etc.alternate_llen):
                try:
                    tf,IP_info=ap.get_a_proxy()
                    if tf:
                        print('in alternate mode get a proxy',IP_info)
                        ap.push_or_discare(IP_info)
                        print('push, or discare')
                except Exception as e:
                    print(e)
                    print ('*******************')
                    time.sleep(10)
                    continue
                else:
                    time.sleep(10)

        else:
            time.sleep(etc.alternate_sleep_time)

def immediate_process():
    ap = Proxy_processing(type='immediate',from_db=etc.alternate_db,to_db=etc.immediate_db)
    while 1:
        if ap.should_add_to_db():
            for i in range(etc.immediate_llen):
                try:
                    tf,IP_info=ap.get_a_proxy()
                    if tf:
                        ap.push_or_discare(IP_info)
                except Exception as e:
                    print(e)
                    continue
        else:
            time.sleep(etc.immediate_sleep_time)
# a = Proxy_processing('alternate',None,etc.immediate_db)
# print(a.get_a_proxy())
alternate_process()