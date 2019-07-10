import redis
pool = redis.ConnectionPool(host='106.12.112.207', password='tongna888')
r = redis.Redis(connection_pool=pool)
repeat = r.scard('person')
# print(repeat)

with open('E://2019-6-26CompanyName/CompanyName.txt', 'r', encoding='utf-8') as f:
    for i in f.readlines():
        name = i.replace('\n', '')
        r.sadd('person', name)
# clearCompany = r.delete('Company_name')
# print(clearCompany)
