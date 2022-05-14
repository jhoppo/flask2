import Creds
import funcs
from db import jh
import requests as req
import datetime
import json
if __name__ == '__main__':
    execDateTime = datetime.datetime.now()
    execDate = execDateTime.strftime("%Y-%m-%d")
    DangChongReq = req.get("https://openapi.twse.com.tw/v1/exchangeReport/TWTB4U")
    if DangChongReq.status_code == 200:
        DangChongList = json.loads(DangChongReq.text)
        del(DangChongReq)
    res = {'oversell': [],
           'sell': [],
           'buy': [],
           'overbuy': [],
           'even': []
           }
    con = jh(**Creds.jhStockCon)
    for i in DangChongList:
        ana = funcs.StockAna(execDate=execDate, n=15, stockID=i['Code'])
        # filter transaction value
        res = ana.mean_transaction()[0][0]
        i.update({"MT": int(res)})
    print(DangChongList)
    # sort dictionary by MT
    print(len(DangChongList))
    ind = 0
    theMax = 0
    theMaxInd = 0
    sortedList = []
    while len(DangChongList) > 0:
        if DangChongList[ind]['MT'] > theMax:
            theMax=DangChongList[ind]['MT']
            theMaxInd= ind
        ind+=1
        if ind == len(DangChongList):
            tmp = DangChongList.pop(theMaxInd)
            sortedList.append(tmp)
            ind = 0
            theMax = 0
            theMaxInd = 0
    print(DangChongList)
    print(sortedList)
    # # cal Rsi
    #     tmp = ana.RSI()
    #     tmpRsi = tmp[i]
    #     if tmpRsi < 30:
    #         res['oversell'].append(tmp)
    #     elif tmpRsi > 30 and tmpRsi < 50:
    #         res['sell'].append(tmp)
    #     elif tmpRsi > 50 and tmpRsi < 70:
    #         res['buy'].append(tmp)
    #     elif tmpRsi > 70:
    #         res['overbuy'].append(tmp)
    #     else:
    #         res['even'].append(tmp)
    # for i,j in res.items():
    #     for vars in j:
    #         for sid, rsi in vars.items():

                # tmpTable = con.query(f"select opening_price, \
                # highest_price, lowest_price, closing_price, \
                # dir, change, highest_price-lowest_price as vibration\
                #  from stock_rawdatav3 where date = '{execDate}' and stock_id = '{sid}'").fetchall()
