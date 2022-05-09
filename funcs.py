import Creds


def fetchTSEList():
    import json
    import requests as req
    try:
        tseList = req.get("https://openapi.twse.com.tw/v1/opendata/t187ap03_L")
    except:
        return "TSE List Failed."
    if tseList.status_code == 200:
        tseList = tseList.text
    tseList = json.loads(tseList)
    dict = {i['公司代號']: i['公司簡稱'] for i in tseList}
    return dict

def SelectionSort(ls,nums, orderByDirection='Ascending'):
    for i in range(len(nums)):
        limit_ind = i
        for j in range(i+1, len(nums)):
            if orderByDirection == 'Ascending':
                if nums[j] < nums[limit_ind]: limit_ind = j
            elif orderByDirection == 'Descending':
                if nums[j] > nums[limit_ind]: limit_ind = j
            else:
                return False

        nums[i], nums[limit_ind] = nums[limit_ind], nums[i]
        ls[i], ls[limit_ind] = ls[limit_ind], ls[i]
    return ls

def invoice():
    from db import jh
    import os
    import requests as req
    from bs4 import BeautifulSoup as bs
    import datetime
    import json
    if datetime.datetime.now().month % 2 == 1 and datetime.datetime.now().day >= 25:
        prizeMonth1 = (datetime.datetime.now() - datetime.timedelta(days=60)).month
        prizeMonth1 = f"0{prizeMonth1}" if prizeMonth1<10 else f"{prizeMonth1}"
        prizeMonth2 = (datetime.datetime.now() - datetime.timedelta(days=30)).month
        prizeMonth2 = f"0{prizeMonth2}" if prizeMonth2<10 else f"{prizeMonth2}"
        prizeYear = (datetime.datetime.now() - datetime.timedelta(days=60)).year
        prizeMonth1 = '01'
        prizeMonth2 = '02'
        fn = f"data/invoice-{prizeYear}-{prizeMonth1}-{prizeMonth2}.txt"
        if os.path.exists(fn):
            return fn
        try:
            webPage = req.get("https://invoice.etax.nat.gov.tw/index.html#")
        except req.exceptions.ConnectionError as err:
            print(f"Error: {err}")
        if webPage.status_code == 200:
            pretty = bs(webPage.text, 'html.parser')
            # numbers
            tables = pretty.findAll('table')[0]
            tables = tables.find_all_next('p')
            prizeNumbers=[]
            for i in tables:
                res = i.text.strip()
                if len(res) == 8 and res not in prizeNumbers:
                    prizeNumbers.append(res)
                elif len(res) == 3 and res not in prizeNumbers:
                    prizeNumbers.append(res)
            dict = {
                "very_special": prizeNumbers[0],
                "special": prizeNumbers[1],
                "first": prizeNumbers[2:5],
                "more": prizeNumbers[5:]
            }
        else:
            print(f"HTTP code error: {webPage.status_code}")
        sql=f"insert into invoice values ('{prizeYear-1911}y{prizeMonth1}-{prizeMonth2}m', '{json.dumps(dict)}');"
        con=jh(**Creds.jhInvoiceCon)
        con.insert(sql)
        con.discon()
        with open(fn, "w", encoding='utf-8') as f:
            f.write(f"1000w\t{dict['very_special']}\n")
            f.write(f"200w\t{dict['special']}\n")
            [f.write(f"20w\t{i}\n") for i in dict['first']]
            [f.write(f"200\t{i}\n") for i in dict['more']]
        return fn
    else:
        ls = os.listdir("./data")
        seq = [ os.stat(f"./data/{i}").st_mtime for i in ls]
        fn = SelectionSort(ls=ls,nums=seq)[-1]
        return fn

