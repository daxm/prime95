#!/usr/bin/python3
"""Find average GHz-Days for recent work done on GIMPS.  http://www.mersenne.org"""

from userdata import *
import requests

main_url = 'http://www.mersenne.org/'
login_url = 'http://www.mersenne.org'
login_data = {'user_login': USERNAME, 'user_password': PASSWORD}

with requests.Session() as session:
    # Access main_url to collect cookies.
    result = session.get(main_url)
    print(result.cookies)
    print(result.headers)


    result = session.post(login_url,
                          data=login_data,
                          )
    print(result.cookies)
    print(result.headers)
