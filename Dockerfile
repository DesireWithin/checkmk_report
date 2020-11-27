FROM harbor.homecredit.cn/hcc/python:3.7.5--alpine-3.10
MAINTAINER CN.D.ITDev-GOV <CN.D.ITDev-GOV@homecredit.cn>

RUN mkdir -p /opt/script /opt/shell/configuration /var/log/hcc-mongo-exporter
COPY requirements.txt hcc_mongo_exporter.py /opt/script/
WORKDIR /opt/script
RUN chmod 755 * && \
    pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

ENTRYPOINT ["python", "hcc_mongo_exporter.py"]
