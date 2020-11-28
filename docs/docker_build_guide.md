## Docker Installation and Yaml Edit

Python获取依赖包
pip freeze > requirements.txt


Docker installation (yum源跳过，使用阿里yum源)
https://docs.docker.com/engine/install/centos/

阿里云yum源添加与Docker安装
```
>>yum install -y yum-utils
>>yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
>>yum install docker-ce docker-ce-cli containerd.io
>>yum list docker-ce --showduplicates | sort -r
>>systemctl start docker
```
if you meet errors like require container-selinux, try below
```
>>yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/container-selinux-2.119.2-1.911c772.el7_8.noarch.rpm
```

Get Started with Docker
https://docs.docker.com/get-started/

Build Your Image
https://docs.docker.com/get-started/part2/

```
>>docker build --tag checkmkreport:1.0 .
```
Run the following command to start a container based on your new image:
```
>>docker run --publish 8000:8080 --detach --name checkmk_report checkmkreport:1.0
```
There are a couple of common flags here:

-- publish asks Docker to forward traffic incoming on the host’s port 8000 to the container’s port 8080. Containers have their own private set of ports, so if you want to reach one from the network, you have to forward traffic to it in this way. Otherwise, firewall rules will prevent all network traffic from reaching your container, as a default security posture.

--detach asks Docker to run this container in the background.

--name specifies a name with which you can refer to your container in subsequent commands, in this case bb.

Visit your application in a browser at localhost:8000. You should see your bulletin board application up and running. At this step, you would normally do everything you could to ensure your container works the way you expected; now would be the time to run unit tests, for example.

Once you’re satisfied that your bulletin board container works correctly, you can delete it:
```
>>docker rm --force checkmk_report
```
The --force option stops a running container, so it can be removed. If you stop the container running with docker stop bb first, then you do not need to use --force to remove it.

配置文件Yaml编写

安装依赖包
```
>>pip install pyyaml
```

https://www.cnblogs.com/qican/p/11773967.html

Yaml文件模板
```yaml
# 简介
name: AnJing
age: 18
profession:
      name: 软件测试工程师
      annual: 3K
skill:
      - name1: 接口测试
        pay: 1K

      - name2: 功能测试
        pay: 2K

```

Python脚本文件测试YML文件
```python

# coding:utf-8
import yaml
import json
# 直接打开读出来
yml_content = open('../checkmk.yml','r',encoding='utf-8')
config = yml_content.read()

# 转换成字典读出来
tmp = yaml.load(config, Loader=yaml.FullLoader)

# 存入JSON文件查看字典结构
json_file = open('../test_scripts/tmp.json', 'w+')
json.dump(tmp, json_file, indent=4)

json_file.close()
print('tmp.json is generated successfully, please check...')
```




