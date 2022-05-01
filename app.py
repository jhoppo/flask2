from flask import Flask, redirect, request, url_for, render_template
import pymysql
from db import db
import Creds
from jhmail import JiehongEmail as je
import datetime
import json

app = Flask(__name__)
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

if __name__ == '__main__':
    app.run('0.0.0.0',debug=True)