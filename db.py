import datetime
class db:
    def __init__(self, **kwargs):
        import pymysql
        self.con = kwargs
        try:
            self.conn = pymysql.connect(**self.con)
        except Exception as ex:
            print(ex)
    def query(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor
    def insert(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.close()
            with open(f"logs/{datetime.datetime.now().strftime('%Y%m%d')}_error.log", "w") as logF:
                logF.write("insert\t"+sql+"\n")
    def discon(self):
        try:
            self.conn.close()
            return "DB Disconnected."
        except:
            return "DB Failed To Disconnect."

class jh:
    def __init__(self, **kwargs):
        import psycopg2
        try:
            self.conn = psycopg2.connect(host=kwargs['host'],
                                         database=kwargs['db'],
                                         user=kwargs['user'],
                                         password=kwargs['password'])
        except Exception as ex:
            print(ex)
    def query(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor
    def insert(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.close()
            with open(f"logs/{datetime.datetime.now().strftime('%Y%m%d')}_error.log", "w") as logF:
                logF.write("insert\t"+sql+"\n")
    def discon(self):
        try:
            self.conn.close()
            return "DB Disconnected."
        except:
            return "DB Failed To Disconnect."