import json
from datetime import datetime, time

import pytz
import requests


def get_number_of_pages(page):
    return page['number_of_pages']                 

def load_pages(url):
    first_page = requests.get(url, params={'page':1}).json()
    yield first_page
    num_of_pages = get_number_of_pages(first_page)
    for page_num in range(2, num_of_pages + 1):
        yield requests.get(url, params={'page':page_num}).json()

def get_time_of_sending(timestamp, timezone):
    utc_datetime = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return utc_datetime.astimezone(pytz.timezone(timezone)).time()

def is_time_in_owl_period(sending_time):
    owl_period = {'start':time(0,0), 'end':time(6,0)}
    return sending_time >= owl_period['start'] and sending_time <= owl_period['end']

def get_all_attempts(url):
    for page in load_pages(url):
            for attempt in page['records']:
                yield attempt

def get_midnighters(attempts):
    midnighters = []
    for attempt in attempts:
        if attempt['timestamp']:
            sending_time = get_time_of_sending(attempt['timestamp'],
                                               attempt['timezone'])
            if is_time_in_owl_period(sending_time):
                midnighters.append(attempt['username'])
    return set(midnighters)


def main(): 
    attempts = get_all_attempts('https://devman.org/api/challenges/solution_attempts/')
    midnighters = get_midnighters(attempts)
    if midnighters:
        print('Found midnighters:')
        for i, user in enumerate(midnighters,1):
            print('{}) {}'.format(i, user))
    else:
        print('Midnighters not found.')        

if __name__ == '__main__':
    main()
