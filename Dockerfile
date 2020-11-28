FROM python:3.7.5
MAINTAINER RYANLLL3<ryanbetough@qq.com>

RUN mkdir -p /opt/checkmk_report/logs
COPY requirements.txt checkmk_report.py checkmk.yml /opt/checkmk_report
WORKDIR /opt/checkmk_report
RUN chmod 777 -R * && \
    pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

ENTRYPOINT ["python3", "checkmk_report.py"]
