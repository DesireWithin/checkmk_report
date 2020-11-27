# coding:utf-8
import yaml
import json
# 直接打开读出来
yml_file = open('../checkmk.yml', 'r', encoding='utf-8')
config_variables = yml_file.read()
# 转换成字典读出来
conf = yaml.load(config_variables, Loader=yaml.FullLoader)

print('CHECKMK_API_URL', conf.get('CHECK_HOST').get('CHECKMK_API_URL'))
print("AUTOMATION_USER", conf.get('CHECK_HOST').get('AUTOMATION_USER'))
print("PASSWORD", conf.get('CHECK_HOST').get('PASSWORD'))
print("MASTER_SITE", conf.get('CHECK_HOST').get('MASTER_SITE'))

print('DB_HOST', conf.get('MYSQL_DB').get('DB_HOST'))
print('DB_PORT', conf.get('MYSQL_DB').get('DB_PORT'))
print('DB_USER', conf.get('MYSQL_DB').get('DB_USER'))
print('DB_PASS', conf.get('MYSQL_DB').get('DB_PASS'))
print('DATABASE', conf.get('MYSQL_DB').get('DATABASE'))
print('DB_CONN_CHAR', conf.get('MYSQL_DB').get('DB_CONN_CHAR'))
print('TABLE', conf.get('MYSQL_DB').get('TABLE'))

# 存入JSON文件查看字典结构
json_file = open('tmp.json', 'w+')
json.dump(conf, json_file, indent=4)

json_file.close()
print('tmp.json is generated successfully, please check...')
