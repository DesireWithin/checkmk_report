# Checkmk Report
## Supported Checkmk Raw Edition (CRE)
https://checkmk.com/download-archive.php?
- 1.6.0
- 1.5.0

Checkmk Raw Edition (CRE) doesn't have report function, like how many hosts are added, 
and in which folder, monitored by which site, so I adopt this solution to export data from 
CheckMK Web API to MYSQL, then add MYSQL to Grafana data source, and create dashboards.

You may git clone the files and build docker image locally for checkmk_report.

This repo only contains 2 scripts as following:
> 1. update_management_address.py - Run it on PC; Bulk edits management address of host. 
>(Require >>pip install check_mk_web_api)
> 2. checkmk_report.py - Build Docker Image; Store Hosts Info to mysql with interval 
>3600 seconds (see checkmk.yml)


## Installation

```
>>yum install git
>>git clone https://github.com/ryanlll3/checkmk_report.git
```

#### Variables configured in checkmk.yml file:
Below variables need to be updated when you are connecting to a new environment. 
Please check the scripts and replace them.
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

REFRESH_INTERVAL:
      SECONDS: 3600
```

### Mysql Preparation Manual: see mysql_installation.md in docs
#### Login mysql
```
>>mysql -u root -p
```
#### Create database for storing the data
```
>>create database checkmk character set utf8;
>>use checkmk;
```
#### Create table in checkmk Database
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
>>yum install docker-ce docker-ce-cli containerd.io  # If errors, see guide below these lines.
>>yum list docker-ce --showduplicates | sort -r
>>systemctl start docker
```
If you meet errors like require container-selinux, try below
```
>>yum install -y http://mirror.centos.org/centos/7/extras/x86_64/Packages/container-selinux-2.119.2-1.911c772.el7_8.noarch.rpm
```
#### Configure Aliyun Image Accelerator
```
>>vim /etc/docker/daemon.json
# Add below 3 lines
{
  "registry-mirrors": ["https://4q8o7k0a.mirror.aliyuncs.com"]
}

>>systemctl daemon-reload
>>systemctl restart docker
```
#### Verify the Python&PIP Installation (Optional)
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
### CheckMK Container Build
#### Docker Image Build
```
>>cd checkmk_report
>>docker build --tag checkmkreport:1.0 .  #.表示当前目录，即包含Dockerfile的目录
# View images
>>docker images
```
#### Container Build and Start
```
>>docker run -it -d -e TZ="Asia/Shanghai" -v /root/checkmk_report/logs/:/opt/checkmk_report/logs --name checkmk_report checkmkreport:1.0
# Check container status
>>docker ps -a
# You may start it again if you found it is in EXIT status, by below command.
>>docker start checkmk_report
```
#### Other Useful Command
```
# View Images
>>docker images
# Remove Images
>>docker rmi image_id
# View All Containers
>>docker ps -a
# Start a Container
>>docker start container_name
# Remove a Container
>>docker rm --force container_name
# View Container Logs
>>docker logs --tail='10' -t container_id  #View latest 10 lines of log
# View Files in Container WorkDIR
>>docker exec container_id ls
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
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/host_count_by_folder.JPG)

CheckMK Hosts Count
```
select count(hostname) from all_hosts where folder like 'main/virtual_server/linux%';
```
All Hosts Grafana Look
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/all_hosts.JPG)
