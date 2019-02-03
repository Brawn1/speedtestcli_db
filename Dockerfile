###################################################
# Dockerfile to run speedtest-cli-db in Docker
# Based on Alpine Linux
###################################################
FROM python:3.6-alpine
MAINTAINER Brawn1

# Configure Timezone
ENV TIMEZONE "Europe/Vienna"
ENV debug false
ENV docker_container true
ENV db-name "speedtestdb.db"
ENV run-test true

RUN apk update &&apk add tzdata
RUN rm -f /etc/localtime && \
    ln -s "/usr/share/zoneinfo/${TIMEZONE}" /etc/localtime && \
    echo "${TIMEZONE}" > /etc/timezone


ENV PRJDIR="speedtestcli_db"
ENV PRJPATH=/$PRJDIR

RUN mkdir -p $PRJPATH/"db"

COPY requirements.txt $PRJPATH/
COPY speedtestcli-db.py $PRJPATH/
COPY setup.py $PRJPATH/

WORKDIR $PRJPATH
RUN pip3 install -r requirements.txt

VOLUME ["$PRJPATH/db"]

CMD ["./speedtestcli-db.py"]
