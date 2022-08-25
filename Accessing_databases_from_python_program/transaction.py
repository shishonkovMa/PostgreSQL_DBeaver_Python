import psycopg2
from datetime import date
from typing import List


def new_reservation(car, start: date, finish: date, driver, pickAt) -> int:
    queryResNr = """select count(*) as overlapping from res 
        where finish between %s and %s or start between %s and %s
        or (start < %s and finish > %s);"""
    queryNewRes = """insert into res(cid, start, finish, pickat, days, did)
        values (%s, %s, %s, %s, %s, %s)
        returning bid;"""
    queryNumInc = """update car
        set res_number = res_number + 1
        where cid = %s;"""
    retValue = 0
    con = psycopg2.connect(database='cars2', user='postgres', password='123', host='localhost')
    cur = con.cursor()
    try:
        cur.execute(queryResNr, (start, finish, start, finish, start, finish))
        oln = cur.fetchone()[0]
        if oln > 0:
            retValue = -1
        else:
            cur.execute(queryNewRes, (car, start, finish, pickAt, (finish-start).days, driver))
            resId = cur.fetchone()[0]
            cur.execute(queryNumInc, (car,))
            cur.close()
            retValue = resId
            con.commit()
    except Exception as err:
        retValue = -1
        con.rollback()
    con.close()
    return retValue


res = new_reservation(6, date(2018, 3, 26), date(2018, 3, 28), 2, 'airport')
