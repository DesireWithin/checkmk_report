FROM python:3.7.5
MAINTAINER RYANLLL3<ryanbetough@qq.com>

RUN mkdir -p /opt/checkmk_report/log
COPY requirements.txt store_all_hosts_to_mysql.py /opt/checkmk_report
WORKDIR /opt/checkmk_report
RUN chmod 755 * && \
    pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

ENTRYPOINT ["python", "store_all_hosts_to_mysql.py"]
