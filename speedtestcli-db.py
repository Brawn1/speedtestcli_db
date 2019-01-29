#!/usr/bin/env python3
###################################################
# Apache License 2.0 Copyright 2017 Günter Bailey #
###################################################
from os import curdir, sep
import os
import sys
import datetime
import sqlite3 as lite
from subprocess import Popen, PIPE
from optparse import OptionParser


DEBUG = False
DB_NAME="speedtestdb.db"
prog_version = "0.1.3"


def create_db():
    if DEBUG:
        print("Create DB: "+str(DB_NAME))
    con = lite.connect(curdir+sep+str(DB_NAME))
    f = open(curdir+sep+"cdb.sql", 'r')
    for x in f:
        con.execute(x)
    con.close()
    f.close()
    if DEBUG:
        print("DB created")


def create_new_db():
    t = '{0:%H%M%S}'.format(datetime.datetime.now())
    d = '{0:%Y-%m-%d}'.format(datetime.datetime.now())
    oldfile = curdir+sep+str(DB_NAME)
    newfile = curdir+sep+str(d+t+"_"+DB_NAME)
    if os.path.isfile(curdir+sep+str(DB_NAME)):
        os.rename(oldfile, newfile)
        print("rename current db to "+str(d+t+"_"+DB_NAME))

    if not os.path.isfile(curdir+sep+str(DB_NAME)):
        check_db()


class database:
    def __init__(self):
        self.connection = lite.connect(curdir+sep+str(DB_NAME))
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
    if not os.path.isfile(curdir+sep+str(DB_NAME)):
        create_db()


class Speedtest:
    def __init__(self):
        self.dbname = DB_NAME
        self.result = dict()
        check_db()
        self.db = database()

    def speedtest(self):
        if DEBUG:
            print("start Speedtest")
        cmd = ["speedtest-cli", "--simple"]
        output = Popen(cmd, stdout=PIPE, stderr=PIPE)
        out1, outerror = output.communicate()
        outdec = out1.decode()
        for x in outdec.split('\n'):
            try:
                if DEBUG:
                    print(x.split(':')[0].strip().lower(), " = ", x.split(':')[1].strip())
                self.result.update({x.split(':')[0].strip().lower(): x.split(':')[1].strip()})
            except IndexError:
                pass

        self.save_todb()

    def get_or_set_unit(self, unit):
        while True:
            squery = """SELECT `unit`.`id` FROM `unit` WHERE `name`='%s';""" % (str(unit))
            d = self.db.idquery(squery)
            if d != None:
                return d[0]
            else:
                ins = """INSERT INTO unit(name) VALUES ('%s');""" %(str(unit))
                self.db.insert(ins)

    def save_todb(self):
        t = '{0:%H:%M:%S}'.format(datetime.datetime.now())
        d = '{0:%Y-%m-%d}'.format(datetime.datetime.now())
        if DEBUG:
            print("store into DB")
        if not len(self.result) >= 3:
            if DEBUG:
                print("No Result = ", self.result)
            exit(0)

        ins = """INSERT INTO speedtest(ping, dl_speed, up_speed, date, time, ping_unit, dl_unit, up_unit) VALUES 
('%s', '%s', '%s', '%s', '%s', '%s', '%s','%s');""" %(self.result["ping"].split(' ')[0],
                                                      self.result["download"].split(' ')[0],
                                                      self.result["upload"].split(' ')[0], d, t,
                                                      self.get_or_set_unit(unit=(self.result["ping"].split(' ')[1])),
                                                      self.get_or_set_unit(unit=(self.result["download"].split(' ')[1])),
                                                      self.get_or_set_unit(unit=(self.result["upload"].split(' ')[1])))

        self.db.insert(ins)
        if DEBUG:
            print("Speedtest Finish")
        print("Speedtest Completed")
        print("=========================")
        print("        Results          ")
        print("-------------------------")
        print("Ping = ", self.result["ping"])
        print("Download = ", self.result["download"])
        print("Upload = ", self.result["upload"])
        print("=========================")


class App():
    def __init__(self):
        usage = "usage: Speedtestcli-db v%s options" %(prog_version)
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
                print("new DB "+str(DB_NAME)+" created")

        except IndexError:
            Speedtest().speedtest()


if __name__ == "__main__":
    app = App()
