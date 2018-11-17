
redis_host = '127.0.0.1'
redis_db = 15
redis_psw = 'redisredis'
redis_port = 6379
verified_url = "www.baidu.com"

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
alternate_sleep_time = 300
immediate_sleep_time = 300

immediate_db = 0
alternate_db = 1

info_list = ['IP','port','anonymity','ptype','locate','resspeed']