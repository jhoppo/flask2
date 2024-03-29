from flask import Flask, redirect, request, url_for, render_template
import pymysql
from db import db, jh
import Creds
from jhmail import JiehongEmail as je
import datetime
import json
import psycopg2

app = Flask(__name__)

@app.route('/jh/stock/rawdata')
def JHStockRawdata():
    return render_template('stockRawdata.html')

@app.route('/jh/stock/rawdata/query', methods=['POST'])
def JHStockRawdataQuery():
    if request.form['startDate'] == '':
        startDate = (datetime.datetime.now() - datetime.timedelta(days=60)).strftime("%Y-%m-%d")
    else:
        startDate = request.form['startDate']
    if request.form['endDate'] == '':
        endDate = datetime.datetime.now().strftime("%Y-%m-%d")
    else:
        endDate = request.form['endDate']
    tHeader = ['date', 'stockID', 'trade_volume', \
               'transaction', 'trade_value', 'open', \
               'high', 'low', 'close', 'dir', \
               'change', 'k_bar_type']
    con = jh(**Creds.jhStockCon)
    contents = con.query(f"select * from stock_rawdatav3 where \
    stock_id = '{request.form['id']}' and \
    date >= '{startDate}' and \
    date <= '{endDate}'").fetchall()
    con.discon()
    return render_template('stockRawdata.html', tHeader=tHeader, contents=contents)

@app.route('/jh/stock/')
def JHStockIndex():
    con = jh(**Creds.jhStockCon)
    cont = con.query("select * from test;").fetchall()
    con.discon()
    print(cont[0])
    return "HI"

@app.route('/stock')
def StockIndex():
    tHeader = ['股票代碼', '每股成本', f'停利點({Creds.stopWin*100}%)', f'停損點({Creds.stopLose*100}%)', '剩餘股數', '目前獲利']
    con = db(**Creds.dbStockCon)
    contents = con.query(f"""select stockID,
 abs(sum(total_amount)/sum(quantity)) as total_cost,
 abs(sum(total_amount)/sum(quantity))*{1+Creds.stopWin} as stop_win, 
 abs(sum(total_amount)/sum(quantity))*{1-Creds.stopLose} as stop_lose,
 sum(quantity) as current_stock,
 sum(total_amount) as current_profit
from `stock`.`transaction` group by stockID;
    """).fetchall()
    con.discon()
    return render_template('stockOrder.html', tHeader=tHeader, contents=contents)

@app.route('/stock/order', methods=['POST'])
def StockOrder():
    # transaction(stockID: str, price: float, quantity: int, dir: str)
    # i = request.form['id']
    # name = request.form['name']
    # submitAction = request.form['submit']
    transaction(stockID=request.form['id'], price=float(request.form['price']), quantity=float(request.form['shares']), dir=request.form['submit'])
    return redirect(url_for('StockIndex'))

@app.route('/req')
def ReqPage():
    return render_template('req.html')

@app.route('/method', methods=['POST', 'GET'])
def TheMethod():
    reqMethod = request.method
    if reqMethod == "POST":
        user = request.form['user']
    else:
        user = request.args.get('user')
    return redirect( url_for('reqSucess', reqM=reqMethod, user=user))

@app.route('/sucess/<reqM>/<user>')
def reqSucess(reqM, user):
    return render_template('success.html', reqM=reqM, user=user)

@app.route('/quitlist')
def QuitList():
    header = open("./data/quitList_header.txt", "r", encoding='utf-8').read().split("\t")
    cont = open("./data/quitList.txt", "r", encoding='utf-8').readlines()
    data = [ row.split("\t") for row in cont]
    return render_template('quitlist.html', tHeader=header, contents=data)

@app.route('/insert')
def Insertion():
    con = db(**Creds.dbCon)
    cont = con.query("select * from testdb").fetchall()
    con.discon()
    return render_template('insert.html', contents=cont)

@app.route('/insert/submit', methods=['POST'])
def InsertionSubmit():
    i = request.form['id']
    name = request.form['name']
    submitAction = request.form['submit']
    if submitAction == 'insert':
        con = db(**Creds.dbCon)
        con.insert(f"insert into testdb values({i}, '{name}')")
        con.discon()
    elif submitAction == 'delete':
        dict = {'id':i, 'name':name}
        where = ''
        for key,val in dict.items():
            if len(val) == 0:
                pass
            else:
                if type(val) == int:
                    where += f'{key}={val}'
                else:
                    where += f"{key}='{val}'"
        if len(where) > 0:
            where = "where "+ where
            print(f"delete {where}")
            con = db(**Creds.dbCon)
            con.insert(f"delete from testdb {where}")
            con.discon()
    return redirect(url_for('Insertion'))

@app.route('/mail')
def CreateMail():
    return render_template('/mail.html')
@app.route('/mail/send', methods=['POST'])
def SendMail():
    if request.form['id'] == '':
        sendCode = "Send Failed. Tell me Who the fuck you are!"
        return render_template('/mail.html', send_result=sendCode)
    if '@' not in request.form['id']:
        sendCode = "Send Failed. Are you fucking idiot? Give me the right mail address !"
        return render_template('/mail.html', send_result=sendCode)
    if request.form['pw'] == '':
        sendCode = "Send Failed. Tell me What the fuck is your password!"
        return render_template('/mail.html', send_result=sendCode)
    if request.form['receivers'] == '':
        sendCode = "Send Failed. Who the fuck is your receiver?! Stop being dump!"
        return render_template('/mail.html', send_result=sendCode)
    senderInfo = {"sender": request.form['id'],
                  "password": request.form['pw'],
                  "mail-subject": request.form['subject'],
                  "mail-body": request.form['body']}
    con = db(**Creds.dbCon)
    cont = con.insert(f"insert into user_info (info) values ('{json.dumps(senderInfo)}')")
    con.discon()
    try:
        sm = je(sender=request.form['id'],
                sender_password=request.form['pw'],
                smtp_host=request.form['smtp'],
                smtp_host_port=request.form['port'])
    except:
        return render_template( 'mail.html', send_result = "Auth failed, mail not sent.")
    sm.MailSubject(request.form['subject'])
    receivers = request.form['receivers'].replace(" ","").split(",")
    sm.SendTo(receivers)
    sm.MailContent(request.form['body'])
    if len(request.form['ccs']) > 0:
        ccs = request.form['ccs'].replace(" ","").split(",")
        sm.CcTo(ccs)
    sendCode = sm.SendMail()
    sm.LogoutsmTP()
    return render_template( 'mail.html', send_result = sendCode)

def transaction(stockID: str, price: float, quantity: int, dir: str):
    # call API to transact
    # the unit of quantity is shares
    # dir is buy or sell
    # if API success, record the transaction into `stock`.`transaction`
    if dir == 'buy':
        taxRatio = 0
    elif dir == 'sell':
        taxRatio = 0.003
        quantity*=-1
    else:
        return 'Wrong values'

    # count the cost
    amount = price * quantity
    fee = round(abs(amount*0.1425/100))
    tax = round(abs(amount*taxRatio))
    total_cost = amount+fee+tax if fee>20 else amount+20+tax
    per_cost = abs(total_cost) / quantity
    transTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = db(**Creds.dbStockCon)
    con.insert(f"insert into transaction values('{transTime}', '{stockID}', {price},\
{quantity}, {-amount}, {tax}, {fee}, {-total_cost}, {abs(per_cost)}, '{dir}');")
    con.discon()
    return
if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)