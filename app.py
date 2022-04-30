from flask import Flask, redirect, request, url_for, render_template
import pymysql
from db import db
import Creds

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
if __name__ == '__main__':
    app.run(debug=True)