#!/usr/bin/python3
"""Find average GHz-Days for recent work done on GIMPS.  http://www.mersenne.org"""

from userdata import *
import requests

main_url = 'http://www.mersenne.org/'
login_url = 'http://www.mersenne.org/account/default.php'
login_data = {'user_login': USERNAME, 'user_password': PASSWORD}

with requests.Session() as session:
    result = session.get(main_url)

    print(result.cookies)
    result = session.post(login_url,
                          data=login_data,
                          headers=dict(referer=main_url),
                          cookies=result.cookies,)
    print(result.cookies)
    print(result.text)
