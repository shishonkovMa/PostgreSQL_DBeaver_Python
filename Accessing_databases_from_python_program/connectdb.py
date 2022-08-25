import psycopg2


def print_all_cars():
    # create a connection
    con = psycopg2.connect(database='cars', user='postgres', password='123', host='localhost')
    # create a client-side cursor
    cur = con.cursor()
    # write a query and execute it
    cur.execute('select cid, make, year from car')
    # loop through the results
    for record in cur:
        # handle the result
        print(record[0], record[1], record[2])  # print column of the record
    con.close()


def print_all_cars_with_resn(resn):
    con = psycopg2.connect(database='cars', user='postgres', password='123', host='localhost')
    cur = con.cursor()
    cur.execute("""select car.cid, year, make 
                   from car join 
                       res using(cid) 
                   group by car.cid, year, make
                   having count(*) >= %s""", [resn])
    for record in cur:
        print(record[0], record[1], record[2])  # print column of the record
    con.close()


print_all_cars_with_resn(0)
