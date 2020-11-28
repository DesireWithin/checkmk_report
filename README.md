# Checkmk Report
## Supported Checkmk versions
- 1.6.0
- 1.5.0

If you want to run the script independently, you need install below package.
###### Following https://github.com/brennerm/check-mk-web-api to install check_mk_web_api first.


This repo only contains 2 scripts as following:
> 1. (update_management_address.py)Bulk edits management address of host.(only run it on your computer)
> 2. (checkmk_report)Store Hosts Info to mysql


## Installation

- With pip
```
>>pip install check_mk_web_api
```

## Preparation for "saving data to mysql(checkmk_report.py)"

### The script "checkmk_report.py" is to STORE CHECKMK HOSTS INTO MYSQL.
Below variables need to be updated when you are connecting to a new environment. Please check the scripts and replace them.

### Variables configured in checkmk.yml file:
```
CHECKMK_API_URL = 'http://check_ip/mysite/check_mk/webapi.py'
AUTOMATION_USER = 'automation'
PASSWORD = 'd5435d51-cfa7-4c18-ae8b-7a924b7eb228'
MASTER_SITE = 'mysite'

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'your_user'
DB_PASS = 'your_password'
DATABASE = 'checkmk'
DB_CONN_CHAR = 'utf8'
TABLE = 'all_hosts'
```

## Mysql preparation reference manual:
### Login mysql
```
>>mysql -u root -p
```

### Create database for storing the data
```
>>create database checkmk character set utf8;
>>use checkmk;
```

### Create table in checkmk db

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


### Create user and grant access
```
>>create user 'your_user'@'%' identified by 'your_password';
>>grant all on *.* to 'your_user'@'%';
>>flush privileges;
>>quit
```

### Install pymysql
```
>>pip install pymysql
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
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/CheckMK_Sites_Capacity.jpg)


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
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/Grafana_dashboard_Look.jpg)

### CheckMK Hosts Count

```
select count(hostname) from all_hosts where folder like 'main/virtual_server/linux%';
```
### Grafana Look
![image](https://github.com/ryanlll3/checkmk_report/blob/master/pictures/Hosts_Info_Grafana.jpg)
