"""
README
You need prepare your python environment.

You need install checkmk web api following below link.
# checkmk web api documentation: https://brennerm.github.io/check-mk-web-api/

you need install pymysql package, by executing below.
pip install pymysql

you need put this script into the checkmk web api folder to make sure the "import" works.

This script is to STORE CHECKMK HOSTS INTO MYSQL.
Below variables need to be updated when you are connecting to a new environment.

variables:
CHECKMK_API_URL = 'http://checkmk_ip/mysite/check_mk/webapi.py'
AUTOMATION_USER = 'automation'
PASSWORD = 'automation_secrets'
MASTER_SITE = 'mysite'

DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'your_user'
DB_PASS = 'your_password'
DATABASE = 'checkmk'
DB_CONN_CHAR = 'utf8'
TABLE = 'all_hosts'

mysql preparation reference manual:
# login mysql
mysql -u root -p

# create database for storing the data
create database checkmk character set utf8;

# select db
use checkmk;

# create table in checkmk db
create table all_hosts (
uuid int primary key auto_increment,
hostname varchar(40) not null,
ip varchar(20),
mgt_ip varchar(20),
folder varchar(50),
monitored_by_site varchar(20),
created timestamp not null);

# create user and grant access
create user 'ryan'@'%' identified by 'ryan';
grant all on *.* to 'ryan'@'%';
flush privileges;

"""

import check_mk_web_api as cmwa
import time
import pymysql


CHECKMK_API_URL = 'http://checkmk_ip/mysite/check_mk/webapi.py'
AUTOMATION_USER = 'automation'
PASSWORD = 'automation_password'
MASTER_SITE = 'your_master_site'

DB_HOST = 'mysql_host_ip'
DB_PORT = 3306
DB_USER = 'your_db_user'
DB_PASS = 'your_password'
DATABASE = 'checkmk'
DB_CONN_CHAR = 'utf8'
TABLE = 'all_hosts'


class CheckMKDB():
    def __init__(self,host=DB_HOST,
                 port=DB_PORT,
                 user=DB_USER,
                 passwd=DB_PASS,
                 charset=DB_CONN_CHAR,
                 database=DATABASE):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.database = database
        self.charset = charset
        self.connect_database()
        self.app = CheckmkAPI(CHECKMK_API_URL, username=AUTOMATION_USER, secret=PASSWORD)

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
        cur.execute(sql1)
        cur.execute(sql2)
        self.db.commit()
        cur.close()

    def store_hosts_to_db(self):
        hosts = self.get_all_hosts()
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
                cur.execute(sql,tmp_list)
                # self.db.commit()
            except Exception as e:
                print('\n# SQL Execute exception',e)
                # self.db.rollback()
        try:
            self.db.commit()
        except Exception as e:
            print('\n# DB Commit exception',e)
            self.db.rollback()
        cur.close()
        print('Job Done. Please check data in DB.')
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
        print('\n# DB Class exception',e)
    except KeyboardInterrupt:
        print('\n# Byebye')
    DB.close()
