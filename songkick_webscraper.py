import sys
import requests
import bs4
import html

if len(sys.argv)<2:
    EVENT_FILE_NAME = "songkick-events.json"
else:
    EVENT_FILE_NAME = sys.argv[1]


base_url = 'https://www.songkick.com'
alphabets = [i for i in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTWXYZ0123456789']

for alphabet in alphabets:
    print('alphabet='+alphabet)
    i = 1
    while True:
        print('i='+str(i))
        res = requests.get(base_url+'/search?page='+str(i)+'&per_page=10&query='+alphabet+'&type=upcoming')
        #print(base_url+'/search?page='+str(i)+'&per_page=10&query='+alphabet+'&type=upcoming')
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

            f = open(EVENT_FILE_NAME, "a")
            f.write("{" +
                    "\"name\":\""+event_name +"\", "+
                    "\"location\":\""+event_location+"\", "+
                    "\"event_url\":\"" + event_link + "\", " +
                    "\"event_date_time\":\"" + event_date + "\"" +
                     "}\n")
            f.close()
        i += 1