#!/usr/bin/python
# -*- coding:utf-8

"""
README
You need prepare your python environment.

You need install checkmk.yml web api following below link.
# checkmk.yml web api documentation: https://brennerm.github.io/check-mk-web-api/

you need install pymysql package, by executing below.
pip install pymysql

you need put this script into the checkmk web api folder to make sure the "import" works.

This script is to STORE CHECKMK HOSTS INTO MYSQL.
Below variables need to be updated when you are connecting to a new environment.

variables in yml file
CHECKMK_API_URL = 'http://checkmk_ip/mysite/check_mk/webapi.py'
AUTOMATION_USER = 'automation'
PASSWORD = 'automation_secrets'
MASTER_SITE = 'mysite'

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'your_user'
DB_PASS = 'your_password'
DATABASE = 'checkmk.yml'
DB_CONN_CHAR = 'utf8'
TABLE = 'all_hosts'

mysql preparation reference manual:
# login mysql
mysql -u root -p

# create database for storing the data
create database checkmk.yml character set utf8;

# select db
use checkmk.yml;

# create table in checkmk.yml db
create table all_hosts (
uuid int primary key auto_increment,
hostname varchar(40) not null,
ip varchar(20),
mgt_ip varchar(20),
folder varchar(50),
monitored_by_site varchar(20),
created timestamp not null);

# create user and grant access
create user 'your_user'@'%' identified by 'your_pass';
grant all on *.* to 'your_user'@'%';
flush privileges;

"""

import check_mk_web_api as cmwa
import time
import pymysql
import yaml
import logging
from logging.handlers import RotatingFileHandler


yml_file = open('checkmk.yml', 'r', encoding='utf-8')
config_variables = yml_file.read()
# 转换成字典读出来
conf = yaml.load(config_variables, Loader=yaml.FullLoader)

CHECKMK_API_URL = conf.get('CHECK_HOST').get('CHECKMK_API_URL')
AUTOMATION_USER = conf.get('CHECK_HOST').get('AUTOMATION_USER')
PASSWORD = conf.get('CHECK_HOST').get('PASSWORD')
MASTER_SITE = conf.get('CHECK_HOST').get('MASTER_SITE')

DB_HOST = conf.get('MYSQL_DB').get('DB_HOST')
DB_PORT = conf.get('MYSQL_DB').get('DB_PORT')
DB_USER = conf.get('MYSQL_DB').get('DB_USER')
DB_PASS = conf.get('MYSQL_DB').get('DB_PASS')
DATABASE = conf.get('MYSQL_DB').get('DATABASE')
DB_CONN_CHAR = conf.get('MYSQL_DB').get('DB_CONN_CHAR')
TABLE = conf.get('MYSQL_DB').get('TABLE')


def setup_log(func):
    """配置日志"""

    # 设置日志的记录等级(# FATAL/CRITICAL = 重大的，危险的(50)
	# WARNING = 警告(40)
	# ERROR = 错误(30)
	# INFO = 信息(20)
	# DEBUG = 调试(10)
    logging.basicConfig(level=20)
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/check_report.log", maxBytes=1024 * 1024 * 100, backupCount=10) #1 KB = 1024 bytes
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(asctime)s %(levelname)s File:%(module)s Line:%(lineno)d Message:%(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象,添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
    def wrapper(*args,**kwargs):
        func(*args,**kwargs)
    return wrapper


class CheckMKDB():
    @setup_log
    def __init__(self,host=DB_HOST,
                 port=DB_PORT,
                 user=DB_USER,
                 passwd=DB_PASS,
                 charset=DB_CONN_CHAR,
                 database=DATABASE):
        logging.info('CheckMK DB Class Initialized.')
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.database = database
        self.charset = charset
        self.connect_database()
        logging.info('Database Connected.')
        self.app = CheckmkAPI(CHECKMK_API_URL, username=AUTOMATION_USER, secret=PASSWORD)
        logging.info('Initialized CheckMK API.')

    def connect_database(self):
        self.db = pymysql.connect(host=self.host,
                                  port=self.port,
                                  user=self.user,
                                  passwd=self.passwd,
                                  database=self.database,
                                  charset=self.charset)

    def get_all_hosts(self):
        return self.app.get_all_hosts()

    def get_folder_site(self,path):
        path = self.app.get_folder(path)
        return path.get("attributes").get("site", MASTER_SITE)

    def clean_data(self):
        sql1 = "delete from %s" % TABLE
        sql2 = "truncate table %s" % TABLE
        cur = self.db.cursor()
        try:
            logging.info('Deleting data from table %s' % TABLE)
            cur.execute(sql1)
        except Exception as e:
            logging.exception(e)
        try:
            logging.info('Truncating table %s' % TABLE)
            cur.execute(sql2)
        except Exception as e:
            logging.exception(e)
        try:
            self.db.commit()
        except Exception as e:
            logging.error(e)
        cur.close()

    def store_hosts_to_db(self):
        hosts = self.get_all_hosts()
        logging.info('Get All Hosts.')
        cur = self.db.cursor()
        for target_key, target_value in hosts.items():
            host_name = target_value.get("hostname")
            ip_address = target_value.get("attributes").get("ipaddress", 'none')
            mgt_ip = target_value.get("attributes").get("management_address", 'none')
            folder = target_value.get("path")
            if target_value.get("attributes").get("site"):
                monitored_on_site = target_value.get("attributes").get("site")
            else:
                monitored_on_site = self.get_folder_site(folder)

            timestamp = target_value.get("attributes").get("meta_data").get("created_at")
            timearray = time.localtime(timestamp)
            created = time.strftime("%Y-%m-%d %H:%M:%S", timearray)

            tmp_list = [host_name,ip_address,mgt_ip,folder,monitored_on_site,created]

            sql = "insert into " + TABLE + "(hostname,ip,mgt_ip,folder,monitored_by_site,created) \
            values (%s,%s,%s,%s,%s,%s)"
            try:
                cur.execute(sql, tmp_list)
                # self.db.commit()
            except Exception as e:
                logging.exception(e)
                # self.db.rollback()
        try:
            logging.info('Inserting Data into Database')
            self.db.commit()
        except Exception as e:
            logging.error('Inserting Data Error ', e)
            self.db.rollback()
        cur.close()
        logging.info('Job Done. Data is stored in database: %s.%s' % (DATABASE, TABLE))
        return 'Job Done'

    def close(self):
        self.db.close()


class CheckmkAPI(cmwa.WebApi):
    def __init__(self, check_mk_url, username, secret):
        super(CheckmkAPI, self).__init__(check_mk_url, username, secret)


if __name__ == '__main__':
    DB = CheckMKDB()
    try:
        DB.clean_data()
        DB.store_hosts_to_db()
    except Exception as e:
        logging.error(e)
    except KeyboardInterrupt:
        logging.info('Exiting')
    DB.close()
