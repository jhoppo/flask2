import Creds
import datetime
import json

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

def fetchTSEList():
    import requests as req
    import json
    try:
        tseList = req.get("https://openapi.twse.com.tw/v1/opendata/t187ap03_L")
    except:
        return "TSE List Failed."
    if tseList.status_code == 200:
        tseList = tseList.text
    tseList = json.loads(tseList)
    dict = {i['公司代號']: i['公司簡稱'] for i in tseList}
    return dict

def RSI(execDate, n, stockID):
    sql = f"select date, closing_price from stock_rawdatav3 where \
    date < '{execDate}' and \
    stock_id = '{stockID}' \
    order by date desc  limit {n} ;"
    con = jh(**Creds.jhStockCon)
    rawtable = con.query(sql).fetchall()
    con.discon()
    if len(rawtable) == n:
        dict = { i:j for i,j in rawtable}
        values = [i for i in dict.values()]
        pos = 0
        neg = 0
        for i in range(len(values)-1,0,-1):
            diff = values[i] - values[i-1]
            if diff > 0:
                pos+=diff
            else:
                neg+=abs(diff)
        A = pos/(n-1)
        B = neg/(n-1)
        rsi = A / (A+B) * 100
        dict = {stockID:rsi}
        return dict
    else:
        return {stockID:-1}

if __name__ == "__main__":
    tseList = fetchTSEList()
    res = {'oversell':[],
           'sell':[],
           'buy':[],
           'overbuy':[],
           'even':[]
           }
    for i in tseList.keys():
        execDate = datetime.datetime.now().strftime("%Y-%m-%d")
        tmp = RSI(execDate=execDate, n=15, stockID=i)
        tmpRsi = tmp[i]
        if tmpRsi<30:
            res['oversell'].append(tmp)
        elif tmpRsi>30 and tmpRsi<50:
            res['sell'].append(tmp)
        elif tmpRsi>50 and tmpRsi<70:
            res['buy'].append(tmp)
        elif tmpRsi>70:
            res['overbuy'].append(tmp)
        else:
            res['even'].append(tmp)
    with open(f"./data/RSI-{execDate}.txt", "w") as f:
        f.write(json.dumps(res))