import psycopg2


def start_planning(year, quarter, user, pwd):
    del_plan_data = f"""delete from plan_data
                        where quarterid = '{year}.{quarter}';"""
    del_plan_status = f"""delete from plan_status
                          where split_part(quarterid, '.', 2)::int = {quarter};"""
    create_plan_status = f"""insert into plan_status
                             select 
                                '{year}.{quarter}'::varchar as quarterid, 
                                'R'::varchar as status, 
                                current_timestamp as modifieddatetime, 
                                '{user}'::varchar as author, countrycode as country
                             from company 
                             group by countrycode;"""
    generate_version_n = f"""insert into plan_data
                             select 
                                'N'::varchar as versionid, t1.country, 
                                '{year}.{quarter}'::varchar as quarterid,
                                t1.pcid, coalesce(avg(t1.salesamt), 0) as salesamt
                             from
                                (select 
                                    t.country,t.quarter_yr,t."year", t.pcid,
                                    sum(t.salesamt) as salesamt
                                from
                                    (select
                                        c.countryregioncode as country, cs.quarter_yr, cs.qr,
                                        cs."year", p.pcid as pcid, cs.salesamt as salesamt
                                    from
                                        country2 c
                                        join company c2 on c2.countrycode = c.countryregioncode
                                        left join company_sales cs on cs.cid = c2.id
                                        join product2 p on p.pcid = cs.categoryid 
                                    where
                                        ((cs."year" = {year} - 1) or (cs."year" = {year} - 2))
                                        and cs.ccls in ('A', 'B')
                                    group by
                                        cs.qr, cs."year", cs.quarter_yr, c.countryregioncode, 
                                        p.pcid, cs.salesamt) as t
                                where 
                                    t.quarter_yr = {quarter}
                                group by 	
                                    t.country,t.quarter_yr,t."year",t.pcid) as t1
                             group by
                                t1.country, t1.pcid"""
    copy_data_from_n_to_p = """insert into plan_data 
                                select
                                    'P'::varchar, country, quarterid, pcid, salesamt
                                from plan_data;"""
    con = psycopg2.connect(database='2022_plans_Mathew', user=user,
                           password=pwd, host='localhost')

    try:
        with con:
            with con.cursor() as cur:
                cur.execute(del_plan_data)
                cur.execute(del_plan_status)
                cur.execute(create_plan_status)
                cur.execute(generate_version_n)
                cur.execute(copy_data_from_n_to_p)
    finally:
        con.close()


start_planning(2014, 1, 'ivan', 'ivan123')


def set_lock(year, quarter, user, pwd):
    change_from_r_to_l = f"""update plan_status
                             set status  = 'L',
                                modifieddatetime = current_timestamp,
                                author = current_user
                             where split_part(quarterid, '.', 1)::int = {year}
                                and split_part(quarterid, '.', 2)::int = {quarter}
                                and status = 'R'
                                and country in (select country
                                                from country_managers
                                                where username = current_user);"""
    con = psycopg2.connect(database='2022_plans_Mathew', user=user,
                           password=pwd, host='localhost')
    try:
        with con:
            with con.cursor() as cur:
                cur.execute(change_from_r_to_l)
    finally:
        con.close()


set_lock(2014, 1, 'kirill', 'kirill123')
set_lock(2014, 1, 'sophie', 'sophie123')


# con = psycopg2.connect(database='2022_plans_Mathew', host='localhost', user='kirill', password='kirill123')
# cur = con.cursor()
# cur.execute("""select *
#                from v_plan_edit""")
# for record in cur:
#     print(record[0], record[1], record[2], record[3], record[4])
# con.close()


def remove_lock(year, quarter, user, pwd):
    change_from_l_to_r = f"""update plan_status
                                 set status  = 'R',
                                    modifieddatetime = current_timestamp,
                                    author = current_user
                                 where split_part(quarterid, '.', 1)::int = {year}
                                    and split_part(quarterid, '.', 2)::int = {quarter}
                                    and status = 'L'
                                    and country in (select country
                                                from country_managers
                                                where username = current_user);"""
    con = psycopg2.connect(database='2022_plans_Mathew', user=user,
                           password=pwd, host='localhost')
    try:
        with con:
            with con.cursor() as cur:
                cur.execute(change_from_l_to_r)
    finally:
        con.close()


remove_lock(2014, 1, 'kirill', 'kirill123')
remove_lock(2014, 1, 'sophie', 'sophie123')


def accept_plan(year, quarter, user, pwd):
    del_plan_data_a = f"""delete from plan_data
                          where quarterid = '{year}.{quarter}'
                                and versionid = 'A'
                                and country in (select country
                                                from country_managers
                                                where username = '{user}');"""
    copy_data_from_p_to_a = f"""insert into plan_data
                                    select 'A', pd.country, pd.quarterid,
                                            pd.pcid, pd.salesamt
                                    from plan_data pd
                                        join plan_status ps on ps.quarterid = pd.quarterid
                                                               and ps.country = pd.country
                                        join country_managers cm on cm.country = ps.country
                                    where
                                        ps.quarterid = ''|| {year} || '.' || {quarter}
                                        and versionid = 'P'
                                        and cm.username = '{user}'
                                        and ps.status = 'R';"""
    change_from_r_to_a = f"""update plan_status
                             set status  = 'A',
                                modifieddatetime = current_timestamp,
                                author = current_user
                             where split_part(quarterid, '.', 1)::int = {year}
                                and split_part(quarterid, '.', 2)::int = {quarter}
                                and status = 'R'
                                and country in (select country
                                                from country_managers
                                                where username = current_user);"""
    con = psycopg2.connect(database='2022_plans_Mathew', user=user,
                           password=pwd, host='localhost')
    try:
        with con:
            with con.cursor() as cur:
                cur.execute(del_plan_data_a)
                cur.execute(copy_data_from_p_to_a)
                cur.execute(change_from_r_to_a)
    finally:
        con.close()


accept_plan(2014, 1, 'kirill', 'kirill123')
accept_plan(2014, 1, 'sophie', 'sophie123')
