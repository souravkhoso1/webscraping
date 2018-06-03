import requests
import json
import pprint
import sys
import os
import ast
import configparser

config = configparser.ConfigParser()
config.read('eventbrite_config.ini')

BASE_URL = "https://www.eventbriteapi.com/v3"
CLIENT_SECRET = config['DEFAULT']['CLIENT_SECRET']
PERSONAL_OAUTH_TOKEN = config['DEFAULT']['PERSONAL_OAUTH_TOKEN']
ANONYMOUS_ACCESS_OAUTH_TOKEN = config['DEFAULT']['ANONYMOUS_ACCESS_OAUTH_TOKEN']

if len(sys.argv)<2:
    EVENT_FILE_NAME = "eventbrite-events.json"
else:
    EVENT_FILE_NAME = sys.argv[1]

CATEGORY_FILE_NAME = "eventbrite_categories.json"

if os.path.isfile(CATEGORY_FILE_NAME):
    f = open(CATEGORY_FILE_NAME, "r")
    categories = ast.literal_eval(f.read())
    #print(type(categories))
    f.close()
else:
    # got all categories under 'categories' dictionary
    categories = []
    continuation = ""
    while True:
        response = requests.get(
            BASE_URL + "/categories/"+("" if len(continuation)==0 else "?continuation="+continuation),
            headers={
                "Authorization": "Bearer " + PERSONAL_OAUTH_TOKEN,
            },
            verify=True,  # Verify SSL certificate
        )
        categories_json = response.json()
        #pprint.pprint(categories_json)
        for category in categories_json['categories']:
            categories.append(category)
        if not categories_json['pagination']['has_more_items']:
            break
        else:
            continuation = categories_json['pagination']['continuation']

    # get category detailed info

    for i in range(len(categories)):
        response = requests.get(
            BASE_URL + "/categories/" + categories[i]['id'],
            headers={
                "Authorization": "Bearer " + PERSONAL_OAUTH_TOKEN,
            },
            verify=True,  # Verify SSL certificate
        )
        category_json = response.json()
        categories[i] = category_json
        print(str(i))

    f = open("eventbrite_categories.json", "w")
    f.write(str(categories))
    f.close()


# pprint.pprint(categories)

def get_keywords(event_json):
    keywords = set()
    category_id = event_json['category_id']
    subcategory_id = event_json['subcategory_id']
    if category_id is not None:
        for category in categories:
            if category['id']==category_id:
                keywords.add(category['name'])
                keywords.add(category['short_name'])
                keywords.add(category['short_name_localized'])
                break
    if subcategory_id is not None:
        for category in categories:
            for subcategory in category['subcategories']:
                if subcategory['id'] == subcategory_id:
                    keywords.add(subcategory['name'])
    return '~'.join(list(keywords))


def validated_json_value(json, *keys):
    val = None
    for key in keys:
        if val is None:
            val = json[key]
        else:
            val = val[key]
        if val is None:
            return ""
    if val is None:
        return ""
    else:
        return val


CITY_LIST = ['Bhubaneswar', 'Bangalore', 'Mumbai', 'Kolkata',
             'Chennai', 'Bengaluru', 'Hyderabad', 'Ahmedabad',
             'Pune', 'Noida', 'Jaipur', 'Kanpur',
             'New Delhi', 'Gurugram', 'Lucknow', 'Kochi'
             'Nagpur', 'Chandigarh', 'Patna', 'Bhopal',
             'Raipur', 'Mangalore', 'Guwahati']

for city in CITY_LIST:
    print(city)
    continuation = ""
    page = 1
    while True:
        response = requests.get(
            BASE_URL+"/events/search/",
            headers = {
                "Authorization": "Bearer "+PERSONAL_OAUTH_TOKEN,
            },
            verify = True,  # Verify SSL certificate
            params= {
                "location.address": city,
                "page": page,
            }
        )

        response_json = response.json()

        #pprint.pprint(response_json)

        for event_json in response_json['events']:
            event_keywords = json.dumps(get_keywords(event_json)).strip("'").strip("\"")
            event_name = validated_json_value(event_json, 'name', 'text').replace("\n", " ").replace("\r", "")
            event_description = validated_json_value(event_json, 'description', 'text').replace("\n", " ").replace("\r", "")
            event_start_time = validated_json_value(event_json, 'start', 'utc')
            event_end_time = validated_json_value(event_json, 'end', 'utc')
            event_joining_fee = ""
            event_url = event_json['url']
            event_img_key = validated_json_value(event_json, 'logo', 'original', 'url')
            event_location = city

            f = open(EVENT_FILE_NAME, "a")
            #f.write("a")
            f.write("{"+
                    "\"keywords\":\""+event_keywords+"\", "+
                    "\"name\":\""+event_name+"\", "+
                    "\"description\":\""+event_description+"\", "+
                    "\"start_time\":\""+event_start_time+"\", "+
                    "\"end_time\":\""+event_end_time+"\", "+
                    "\"joining_fee\":\""+event_joining_fee+"\", "+
                    "\"url\":\""+event_url+"\", "+
                    "\"img_key\":\""+event_img_key+"\", "+
                    "\"location\":\""+event_location+"\""+
                    "}\n")
            f.close()

        print(response_json['pagination'])
        if response_json['pagination']['page_number'] == response_json['pagination']['page_count'] :
            break
        else:
            page = page + 1

    #pprint.pprint(response_json)
