
Checkmk Web Api documentation: https://brennerm.github.io/check-mk-web-api/

[与本文档无关]JSON查看小工具： https://oktools.net/json

[与本文档无关]linux python virtual env preparation https://mp.weixin.qq.com/s/TfIJyelHMRneXVkp09EVlQ

### windows 环境准备如下
VS Code Installation (Ref. VSCodeUserSetup-x64-1.51.1.exe)[可选]

### git Installation (Ref. Git-2.29.2.2-64-bit.exe)

git installation guide: https://blog.csdn.net/qq_32786873/article/details/80570783

git download: https://git-scm.com/downloads

python 3.7 Installation - https://www.python.org/ftp/python/3.7.9/python-3.7.9.exe

系统环境变量添加control panel - 系统 - 高级系统设置 - 环境变量 - 系统变量 - Path - Edit 新增下面两个
c:\users\ryan.liutj\appdata\local\programs\python\python37
c:\users\ryan.liutj\appdata\local\programs\python\python37\Scripts

Open git bash and test with following 2 commands to verify the installation:
```
>>python --version
>>pip --version
```
If pip is not found, please follow below guide to install pip.

```
>>pip installation guide - https://pip.pypa.io/en/stable/installing/

```
Open git bash 
```
>>curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
>>python get-pip.py
```

Test python --V and pip -V again to verify the installation

#### Preparation for checkmk web api - Excel Report
open git bash
```
>>git clone https://github.com/brennerm/check-mk-web-api
>>cd check-mk-web-api
>>python setup.py install
```

```python
import json
import check_mk_web_api

api = check_mk_web_api.WebApi(checkmk_url,
                              username='automation',
                              secret='your_automation_password')

all_hosts = api.get_all_hosts()
f1 = open('all_hosts.json', 'w+')
json.dump(all_hosts,f1,indent=4)
f1.flush()
f1.seek(0,0)
print('all_hosts.json is generated successfully, please check...')
```

Run the script and find the new file generated named "all_hosts.json", then verify whether it is correct.
You may use https://oktools.net/json to read the json file

#### Following steps are for export json files to excel report
```
>>pip install tablib[all]
```

#### Create a new python file and paste following:

```python

import pandas as pd
import check_mk_web_api as cmwa
import json
api = cmwa.WebApi('http://checkmk_ip/mysite/check_mk/webapi.py',
                              username='automation',
                              secret='automation_secrets')
all_hosts = api.get_all_hosts()
data = {
    'host_name': [],
    'ipaddress': [],
    'monitored_on_site': []
}
for target_key, target_value in all_hosts.items():
    data['host_name'].append(target_value.get("hostname"))
    data['ipaddress'].append(target_value.get("attributes").get("ipaddress"))
    data['monitored_on_site'].append(target_value.get("attributes").get("site"))
df = pd.DataFrame(data)
df.to_excel('check_host_list.xls', index=None)
```

#### find the file "check_host_list.xls"

checkmk host 的monitored on site信息，如果在host自己的配置没有勾选，则无法导出 monitored on site的信息，默认值也取决于上一级folder
"""