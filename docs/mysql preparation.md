"""
# server preparation:
# find temp password

# 找回密码
vim /etc/my.cnf
添加skip-grant-tables
systemctl restart mysqld
mysql -u root
update mysql.user set authentication_string="" where user="root";
flush privileges;
重新登录不需要密码

# option 1:

如果之前装过，可以删除
yum remove -y mysql*
rm -rf /var/lib/mysql

开始
mkdir -p /usr/local/mysql

wget https://dev.mysql.com/get/mysql80-community-release-el7-1.noarch.rpm
yum localinstall mysql80-community-release-el7-1.noarch.rpm
yum install mysql-community-server
systemctl start mysqld
cat /var/log/mysqld.log | grep password
mysql -u root -p

set global validate_password.policy=0;
set global validate_password.length=1;
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';

create user 'ryan'@'%' identified by 'ryan';
grant all on *.* to 'ryan'@'%';
user mysql;
update user set plugin='mysql_native_password' where user='ryan';
flush privileges;





# option 2:
yum install -y mariadb-server
systemctl start mariadb
mysqladmin -u root password 'root'


# 登录数据库
mysql -u root -p

create database checkmk charset=utf8;

use checkmk;

create table all_hosts (
uuid int primary key auto_increment,
hostname varchar(40) not null,
ip varchar(20),
mgt_ip varchar(20),
folder varchar(50),
monitored_by_site varchar(20),
created datetime not null);

create user 'ryan'@'%' identified by 'ryan';
grant all on checkmk.* to 'ryan'@'%';
flush privileges;


# back to client:
pip install pymysql
"""


mysql query:



