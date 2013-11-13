import sqlite3
import time
import pytz
import dateutil
import datetime
import hashlib
import random
import ConfigParser
import string,os, sys
import json

from xml.dom import minidom

class tools:

    @staticmethod
    def get_conn():
        con = sqlite3.connect('sql/sqlite.db')
        return con

    @staticmethod
    def get_sql(id_):
        s_sql = ""
        xml = minidom.parse(file="sql.xml")
        dom = xml.getElementById(id=id_)
        s_sql = dom.childNodes[0].nodeValue
        return s_sql

    @staticmethod
    def list_2_tree(_list):
        a_return = []
        i = 0
        while i < len(_list):
            item = _list[i]
            i += 1
            i_len = len(item["code"])
            if i_len == 2:
                a_return.append(item)
                continue

            aa = []
            aa.append(a_return)
            i2 = 2
            while i2 < i_len:
                a = aa[-1]
                p = len(a) - 1
                item2 = a[p]
                if 'children' in item2:
                    print "-"
                else:
                    item2["children"] = []
                aa.append(item2["children"])
                i2 += 2
            aa[-1].append(item)

            i3 = len(aa)-1
            while i3 > 0:
                aa[i3-1][len(aa[i3-1])-1]["children"] = aa[i3]
                i3 -= 1
        return a_return

    @staticmethod
    def read_language_from_ini():
        data = {}
        list_dirs = os.walk("static/language/en/")
        for root, dirs, files in list_dirs:
            for f in files:
                data2 = {}
                path = os.path.join(root, f)
                filename = f[:-4]
                cf = ConfigParser.ConfigParser()
                cf.read(path)
                s = cf.sections()
                v = cf.items(s[0])
                for _array in v:
                    data2[_array[0]] = _array[1].replace("\"", "")
                data[filename] = data2
        print(data)
        return data

    @staticmethod
    def set_language_json():
        data = tools.read_language_from_ini()
        str = json.dumps(data)

        file_object = open('static/language/json.js', 'w')
        file_object.write("var il8n="+str+";")
        file_object.close()

    @staticmethod
    def set_basic_parameter_json():
        conn = tools.get_conn()
        sql = tools.get_sql("basic_parameter__json")
        cursor = conn.cursor()
        cursor.execute(sql)
        data = {}
        reference = ""
        for row in cursor:
            reference_ = row[2]
            if reference != reference_:
                reference = reference_
                data[reference] = {}
            data[reference][row[0]] = row[1]
        str = json.dumps(data)
        file_object = open('static/js/basic_parameter_data.js', 'w')
        file_object.write("var basic_parameter_data="+str+";")
        file_object.close()

if __name__ == "__main__":
    #tools.get_sql("basic_user__session_update")
    tools.set_basic_parameter_json()
