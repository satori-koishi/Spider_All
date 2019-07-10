# import pymongo
#
# myclient = pymongo.MongoClient("mongodb://192.168.31.154:27017/")
#
# mydb = myclient["mydatabase"]
#
# myclient = pymongo.MongoClient("mongodb://192.168.31.154:27017/")
# mydb = myclient["mydatabase"]
#
# mycol = mydb["customers"]
#
# mydict = {"name": "John", "address": "Highway 37"}
#
# x = mycol.insert_one(mydict)
# from pymongo import MongoClient
#
# client = MongoClient('mongodb://admin:tongna888@106.12.113.52:27017/')
#
# mydb = client["CreditChina"]["CompanyBasicInfo"]
#
# mydict = {'companyName': '西安东旭景观建设工程有限公司', 'liceNumber': '91610103566037945B', 'departmentNumber': '610100100391825', 'organizationCode': None, 'taxNumber': None, 'legalName': '吴磊', 'legalIdCard': '6101241985*****518', 'address': '西安市碑林区劳卫路1号西荷花园4号楼20层5号房'}
#
# xx = mydb.insert_one(mydict)
# print(xx)


import sys

# make a copy of original stdout route
stdout_backup = sys.stdout
# define the log file that receives your log info
log_file = open("message.log", "w")
# redirect print output to log file
sys.stdout = log_file

print("Now all print info will be written to message.log")
# any command line that you will execute
...

log_file.close()
# restore the output to initial pattern
sys.stdout = stdout_backup

print("Now this will be presented on screen")