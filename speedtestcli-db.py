#!/usr/bin/env python3
###################################################
# Apache License 2.0 Copyright 2017 Günter Bailey #
###################################################
from os import curdir, sep, getenv, mkdir, path, rename
import json
import sys
import datetime
import sqlite3 as lite
from subprocess import Popen, PIPE
from optparse import OptionParser


DEBUG = True if getenv('debug', 'False') == 'True' else False
DB_NAME = getenv('db_name', 'speedtestdb.db')
DB_PATH = curdir+sep+'db'
prog_version = '1.0'

CREATE_DB = ['CREATE TABLE "speedtest" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "ping" FLOAT, "dl_speed" FLOAT, "up_speed" FLOAT, "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP, "ping_unit" INTEGER, "dl_unit" INTEGER, "up_unit" INTEGER);',
             'CREATE TABLE "unit" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" TEXT NOT NULL  UNIQUE );']

CREATE_VIEW = ['CREATE VIEW `group_date_min_view` AS select min(ping), min(dl_speed), min(up_speed), date(timestamp) from speedtest group by date(timestamp) order by date(timestamp);',
               'CREATE VIEW `group_date_view` AS select ping, dl_speed, up_speed, date(timestamp) from speedtest group by date(timestamp) order by date(timestamp);',
               'CREATE VIEW `max_group_date_view` AS select max(ping), max(dl_speed), max(up_speed), date(timestamp) from speedtest group by date(timestamp) order by date(timestamp);']


def create_db_dir():
    if not path.exists(DB_PATH):
        mkdir(DB_PATH)


def create_db():
    if DEBUG:
        print("Create DB: {}".format(DB_NAME))
    con = lite.connect(DB_PATH+sep+DB_NAME)
    dbcreatelist = CREATE_DB + CREATE_VIEW
    for x in dbcreatelist:
        con.execute(x)
    con.close()
    if DEBUG:
        print("DB created")


def create_new_db():
    dt = '{0:%Y-%m-%d_%H%M%S}'.format(datetime.datetime.now())
    oldfile = DB_PATH+sep+'{}'.format(DB_NAME)
    newfile = DB_PATH+sep+'{}_{}'.format(dt, DB_NAME)
    if path.isfile(DB_PATH+sep+str(DB_NAME)):
        rename(oldfile, newfile)
        print("rename current db to {}_{}".format(dt, DB_NAME))

    if not path.isfile(DB_PATH+sep+'{}'.format(DB_NAME)):
        check_db()


class database():
    def __init__(self):
        self.connection = lite.connect(DB_PATH+sep+'{}'.format(DB_NAME))
        self.cursor = self.connection.cursor()

    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            self.connection.rollback()

    def query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.rollback()
        return cursor.fetchall()

    def idquery(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.rollback()
        return cursor.fetchone()

    def __del__(self):
        self.connection.close()


def check_db():
    if not path.exists(DB_PATH):
        create_db_dir()
    if not path.isfile(DB_PATH+sep+'{}'.format(DB_NAME)):
        create_db()


class Speedtest:
    def __init__(self):
        self.result = dict({'meta_server': dict(), 'meta_client': dict(), 'version': str(prog_version)})
        check_db()
        self.db = database()
        self.msg = """Speedtestcli-db {version} Completed\n=========================\nResults
-------------------------\nPing = {ping} {ping_unit}\nDownload = {dl_speed} {dl_unit}
Upload = {up_speed} {up_unit}\n========================="""

    def cv_humanreadable(self, size=0):
        """
        convert bit/s into human readable size
        2**10 = 1024
        :param size: bit/s float or integer
        :return: tupple (<float round 2 decimal places>, <unit>)
        """
        power = 2**10
        n = 0
        powern = dict({0: 'bit/s', 1: 'Kbit/s', 2: 'Mbit/s', 3: 'Gbit/s', 4: 'Tbit/s'})
        while size > power:
            size /= power
            n += 1
        return '{0:.2f}'.format(size), powern.get(n, 'bit/s')

    def print_msg(self):
        """
        format and print result
        :return:
        """
        print(self.msg.format(**self.result))

    def speedtest(self):
        if DEBUG:
            print("start Speedtest")
        cmd = ["speedtest-cli", "--json"]
        output = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out1, outerror = output.communicate()
        outdec = out1.decode()
        jsdata = outdec.split('\n')[0]
        data = json.loads(jsdata)
        self.result.update({'dl_speed': self.cv_humanreadable(size=data.get('download', 0))[0],
                            'dl_unit': self.cv_humanreadable(size=data.get('download', 0))[1],
                            'up_speed': self.cv_humanreadable(size=data.get('upload', 0))[0],
                            'up_unit': self.cv_humanreadable(size=data.get('upload', 0))[1],
                            'ping_unit': 'ms', 'ping': data.get('ping', -99)})
        self.result['meta_server'] = data.get('server', '')
        self.result['meta_client'] = data.get('client', '')
        self.save_todb()

    def get_or_set_unit(self, unit):
        c = 0
        while c < 2:
            squery = """SELECT `unit`.`id` FROM `unit` WHERE `name`='{}';""".format(unit)
            d = self.db.idquery(squery)
            if d:
                return d[0]
            else:
                ins = """INSERT INTO unit(name) VALUES ('{}');""".format(unit)
                self.db.insert(ins)
            c += 1

    def save_todb(self):
        if DEBUG:
            print("store into DB")
        if not len(self.result) >= 3:
            if DEBUG:
                print("No Result = ", self.result)
            exit(0)

        # store unitname for later use
        cache = dict({'dl_unit': self.result['dl_unit'], 'up_unit': self.result['up_unit'],
                      'ping_unit': self.result['ping_unit']})
        # convert unit to foreign Key
        self.result.update({'dl_unit': self.get_or_set_unit(self.result['dl_unit']),
                            'up_unit': self.get_or_set_unit(self.result['up_unit']),
                            'ping_unit': self.get_or_set_unit(self.result['ping_unit'])})

        ins = """INSERT INTO speedtest(ping, dl_speed, up_speed, ping_unit, dl_unit, up_unit) VALUES 
        ({ping}, {dl_speed}, {up_speed}, {ping_unit}, {dl_unit}, {up_unit});""".format(**self.result)

        self.db.insert(ins)
        if DEBUG:
            print("Speedtest Finish")
        # restore unitname
        self.result.update(cache)
        self.print_msg()


class App():
    def __init__(self):
        usage = "Speedtestcli-db v{}".format(prog_version)
        parser = OptionParser(usage=usage)
        parser.add_option("--run-test", action="store_true", default=False, dest="runtest",
                          help="run Speedtest and store result into DB")
        parser.add_option("--create-db", action="store_true", default=False, dest="createdb",
                          help="rename old database if exists and create new one")
        (options, args) = parser.parse_args()

        try:
            if options.runtest:
                Speedtest().speedtest()

            if options.createdb and not options.runtest:
                create_new_db()
                print("new DB {} created".format(DB_NAME))

        except IndexError:
            Speedtest().speedtest()


if __name__ == "__main__":
    app = App()
