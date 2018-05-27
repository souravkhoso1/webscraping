import requests
import bs4
import pymysql
import html

# Open database connection
db = pymysql.connect("localhost","root","","webscraping" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

base_url = 'https://www.songkick.com'
alphabets = [i for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTWXYZ0123456789']

for alphabet in alphabets:
    print('alphabet='+alphabet)
    i = 1
    while True:
        print('i='+str(i))
        res = requests.get(base_url+'/search?page='+str(i)+'&per_page=10&query='+alphabet+'&type=upcoming')
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        events = soup.select('.concert.event')
        if len(events)==0:
            break

        for j in soup.select('.concert.event'):
            #print('Date:'+j.select('.subject')[0])
            event_date = html.escape(j.select('.subject')[0].select('.date')[0].text.strip())
            event_link = html.escape(base_url + j.select('.subject')[0].select('a')[0].get('href'))
            event_name = html.escape(j.select('.subject')[0].select('a')[0].text.strip())
            event_location = html.escape(j.select('.subject')[0].select('.location')[0].text.strip())

            select_sql = """ SELECT id FROM events where event_name='{0}' and event_location='{1}' and 
            event_link='{2}' and event_date='{3}' """.format(event_name, event_location, event_link, event_date)


            insert_sql = """ INSERT INTO events (event_name, event_location, event_link, event_date)
            VALUES ('{0}', '{1}', '{2}', '{3}') """.format(event_name, event_location, event_link, event_date)

            try:
                cursor.execute(select_sql)
                results = cursor.fetchall()
                if len(results)==0:
                    # Execute the SQL command
                    cursor.execute(insert_sql)
                    # Commit your changes in the database
                    db.commit()
                #print("Data inserted")
            except Exception as e:
                print(insert_sql)
                # Rollback in case there is any error
                db.rollback()
                #print("Rollback occured")
        i += 1


# disconnect from server
db.close()