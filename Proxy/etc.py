
redis_host = '127.0.0.1'
redis_db = 0
redis_psw = 'redisredis'
redis_port = 6379

inha_url = 'http://www.kuaidaili.com/free/inha/{}/'
intr_url = 'www.kuaidaili.com/free/intr/{}/'
# verified_url = "http://www.baidu.com"
verified_url = "http://www.baidu.com"
test_url = 'http://www.baidu.com/s?wd=ip'
# 数据库中代理的有效时间
alternate_effective_time = 60*60*24
immediate_effective_time = 300
to_use_effective_time = 300

#alternate queue中的最少数据和每次更新的个数
alternate_mlen = 200
alternate_llen = 2000
#immediate queue中的最少的数据和每次更新的个数
immediate_mlen = 20
immediate_llen = 200

crawl_mlen = 1000
crawl_llen = 10000
alternate_sleep_time = 10
immediate_sleep_time = 10

immediate_db = 0
alternate_db = 1
crawl_db = 2

info_list = ['IP','port','anonymity','ptype','locate','resspeed']