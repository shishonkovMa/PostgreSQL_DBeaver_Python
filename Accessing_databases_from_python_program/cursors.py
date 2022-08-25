import psycopg2


def print_cars_ren(nbooked: int):
    con = psycopg2.connect(database='cars', host='localhost', user='postgres', password='123')
    cur = con.cursor('c')
    cur.execute("""select car.cid, year, make 
                   from car join 
                       res using(cid) 
                   group by car.cid, year, make
                   having count(*) >= %s""", [nbooked])
    cur.itersize = 1
    # for record in cur:
    #     print(record[0], record[1], record[2])
    # con.close()
    record = cur.fetchone()
    while record:
        print(record[0], record[1], record[2])
        record = cur.fetchone()
    con.close()


print_cars_ren(0)
