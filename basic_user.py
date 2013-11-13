import os
import time
import datetime
import pytz


from tools import *

class basic_user:

    @staticmethod
    def call_function( web_data):
        function_name = web_data.get("function")
        t_return = {'status': 2, 'msg': 'no such function'}
        if function_name == "login":
            username = web_data.get("username")
            password = web_data.get("password")
            ip = ""
            client = ""
            gis_lat = ""
            gis_lot = ""
            t_return = basic_user.login(username, password, ip, client, gis_lat, gis_lot)
        elif function_name == "grid":
            t_return = basic_user.grid()
        return t_return

    @staticmethod
    def grid(search,pagesize,pagenum,executor,sortname,sortorder):
        t_return = {'status': 2, 'msg': 'wrong'}
        return t_return

    @staticmethod
    def login(username, md5_time_password, ip, client, gis_lat, gis_lot):
        t_return = {'status': 2, 'msg': 'login failed'}
        con = tools.get_conn()
        cursor = con.cursor()
        failed = False
        s_sql = tools.get_sql("basic_user__login_check")
        s_sql = s_sql.replace("__username__", username)
        results = cursor.execute(s_sql)
        try:
            tz = pytz.timezone("Asia/Shanghai")
            s_hour = datetime.datetime.fromtimestamp(time.time()).strftime('%H')
            i_hour = int(s_hour)
            first_row = results.next()
            r_columns = cursor.description
            if username != "guest":
                s_password = first_row[1]
                s_password_md5 = hashlib.new("md5", s_password+s_hour).hexdigest()
                s_password_md5_2 = hashlib.new("md5", s_password+str(i_hour-1)).hexdigest()
                if (md5_time_password != s_password_md5) and (md5_time_password != s_password_md5_2):
                    failed = True
                    t_return["msg"] = "wrong password"
                    print(s_password_md5_2+" "+s_password_md5+" "+s_password)

            if failed is False:
                t_return["status"] = 1
                t_return["msg"] = "ok"
                if (first_row[9] is not None) and (first_row[11] != "guest"):
                    t_return["msg"] = "kick off"
                    t_return["status"] = 3
                t_data = {}
                s_session = hashlib.new("md5", str(random.random()*100000)).hexdigest()
                t_data.setdefault("session", s_session)
                i = 0
                while i < len(r_columns):
                    t_data.setdefault(r_columns[i][0], first_row[i])
                    i += 1
                cursor.close()

                cursor = con.cursor()
                sql_checkout = tools.get_sql("basic_user__login_logout")
                sql_checkout = sql_checkout.replace("__user_code__", username)
                cursor.execute(sql_checkout)
                con.commit()
                sql_update_session = tools.get_sql("basic_user__login_session")
                sql_update_session = sql_update_session.replace("__username__", username)
                sql_update_session = sql_update_session.replace("__permissions__", basic_user.get_permission(username, con))
                sql_update_session = sql_update_session.replace("__session__", s_session)
                sql_update_session = sql_update_session.replace("__ip__", ip)
                sql_update_session = sql_update_session.replace("__client__", client)
                sql_update_session = sql_update_session.replace("__gis_lat__", gis_lat)
                sql_update_session = sql_update_session.replace("__gis_lot__", gis_lot)
                cursor.execute(sql_update_session)
                con.commit()

                t_data["session"] = hashlib.new("md5", s_session+s_hour).hexdigest()
                t_return["logindata"] = t_data

                cursor.close()
                con.close()

                t_return["permissions"] = basic_user.get_permission_tree(username)
        except StopIteration as e:
            t_return["msg"] = "wrong username"
            failed = True

        return t_return

    @staticmethod
    def get_permission(username, conn):
        s_return = ""
        sql = tools.get_sql("basic_user__getPermission")
        sql = sql.replace("__username__", username)
        cursor = conn.cursor()
        cursor.execute(sql)
        codes = ""
        for row in cursor:
            codes += row[0]+","
        s_return = codes[:-1]
        return s_return

    @staticmethod
    def get_permission_tree(username):
        a_return = []
        conn = tools.get_conn()
        sql = tools.get_sql("basic_user__getPermission")
        sql = sql.replace("__username__", username)
        cursor = conn.cursor()
        cursor.execute(sql)
        r_columns = cursor.description

        for row in cursor:
            t_data = {}
            i = 0
            while i < len(r_columns):
                t_data.setdefault(r_columns[i][0], row[i])
                i += 1
            a_return.append(t_data)

        cursor.close()
        conn.close()
        a_return = tools.list_2_tree(a_return)
        return a_return

if __name__ == "__main__":
    print(basic_user.login("admin","","","","",""))