# coding:utf-8
import yaml
import json
# 直接打开读出来
yml_content = open('../checkmk.yml', 'r', encoding='utf-8')
config = yml_content.read()

# 转换成字典读出来
tmp = yaml.load(config, Loader=yaml.FullLoader)

# 存入JSON文件查看字典结构
json_file = open('tmp.json', 'w+')
json.dump(tmp, json_file, indent=4)

json_file.close()
print('tmp.json is generated successfully, please check...')
