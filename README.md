# Checkmk Report
## Supported Checkmk versions
- 1.6.0
- 1.5.0

This repo only contains 2 scripts as following:
> 1. (update_management_address.py)Bulk edits management address of host.(only run it on your computer)
> 2. (checkmk_report)Store Hosts Info to mysql


## Installation

```
>>yum install git
>>git clone https://github.com/ryanlll3/checkmk_report.git
```
### Preparation for "saving data to mysql(checkmk_report.py)"

#### The script "checkmk_report.py" is to STORE CHECKMK HOSTS INTO MYSQL.
Below variables need to be updated when you are connecting to a new environment. Please check the scripts and replace them.

#### Variables configured in checkmk.yml file:
```
# Variables will be used by python scripts
NAME: CheckMK Configuration
CHECKMK_Version: OMD - Open Monitoring Distribution Version 1.6.0p18.cre
CHECK_HOST:
      CHECKMK_API_URL: 'http://192.168.19.8/mysite/check_mk/webapi.py'
      AUTOMATION_USER: 'automation'
      PASSWORD: 'd5435d51-cfa7-4c18-ae8b-7a924b7eb228'
      MASTER_SITE: 'mysite'

MYSQL_DB:
      DB_HOST: '192.168.19.5'
      DB_PORT: 3306
      DB_USER: 'ryan'
      DB_PASS: 'ryan'
      DATABASE: 'checkmk'
      DB_CONN_CHAR: 'utf8'
      TABLE: 'all_hosts'
```

### Mysql preparation reference manual:
#### Login mysql
```
>>mysql -u root -p
```

#### Create database for storing the data
```
>>create database checkmk character set utf8;
>>use checkmk;
```

#### Create table in checkmk db

```
>>create table all_hosts (
uuid int primary key auto_increment,
hostname varchar(40) not null,
ip varchar(20),
mgt_ip varchar(20),
folder varchar(50),
monitored_by_site varchar(20),
created datetime not null);
```

#### Create user and grant access
```
>>create user 'your_user'@'%' identified by 'your_password';
>>grant all on *.* to 'your_user'@'%';
>>flush privileges;
>>quit
```
### Docker Installation
Ref.
https://docs.docker.com/engine/install/centos/

```
>>yum install -y yum-utils
>>yum-config-manager --add-repo http://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
>>yum install docker-ce docker-ce-cli containerd.io
>>yum list docker-ce --showduplicates | sort -r
>>systemctl start docker
```
If you meet errors like require container-selinux, try below
```
>>yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/container-selinux-2.119.2-1.911c772.el7_8.noarch.rpm
```
#### 配置阿里云镜像加速器
```
# 针对Docker客户端版本大于 1.10.0 的用户
# 您可以通过修改daemon配置文件/etc/docker/daemon.json来使用加速器
# 打开文件添加下面3行
{
  "registry-mirrors": ["https://4q8o7k0a.mirror.aliyuncs.com"]
}

>>systemctl daemon-reload
>>systemctl restart docker
```
#### Verify the Python&PIP Installation
```
>>python --version
>>pip --version
```
If pip is not found, please follow below guide to install pip or execute below command.
https://pip.pypa.io/en/stable/installing/
```
>>curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
>>python get-pip.py
```
#### Docker Image Build
```
>>cd checkmk_report
>>mkdir logs
>>docker build --tag checkmkreport:1.0 .  #.表示当前目录，即包含Dockerfile的目录
# 查看镜像
>>docker images
```
#### 创建容器并启动
```
>>docker run -it -d -e TZ="Asia/Shanghai" -v /root/checkmk_report/logs/:/opt/checkmk_report/logs --name checkmk_report checkmkreport:1.0
# 查看容器
>>docker ps -a
>>docker start checkmk_report
```
#### Other Useful Command
```
# 查看镜像
>>docker images
# 删除镜像
>>docker rmi image_id
# 查看日志
>>docker logs --tail='10' -t container_id  #查看最新10行的log
# 查看容器
>>docker ps -a
# 启动容器
>>docker start container_name
# 删除容器
>>docker rm --force container_name
```

## SQL Selects for Grafana Panel

### CheckMK Capacity
```
SELECT
sysdate() as time,
count(hostname) as value,
monitored_by_site as metric
FROM all_hosts
GROUP BY monitored_by_site
```
### Grafana Look
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/site_capacity1.JPG)
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/site_capacity2.JPG)

### CheckMK Folder
```
SELECT
sysdate() as time,
count(hostname) as value,
folder as metric
FROM all_hosts
GROUP BY folder
```
### Grafana Look
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/host_count_by_folder.jpg)

CheckMK Hosts Count
```
select count(hostname) from all_hosts where folder like 'main/virtual_server/linux%';
```
All Hosts Grafana Look
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/all_hosts.jpg)
