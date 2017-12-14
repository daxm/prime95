#!/usr/bin/python3

from bs4 import BeautifulSoup as bs
import pandas as pd
from lxml import html
from userdata import *
import requests

# ### Possible changeable data ### #
url = 'https://www.mersenne.org'
# results_limit can be anything from '1' to '9999'.
results_limit = '9999'
# ### #


def get_html_content(session, url, **kwargs):
    if 'data' in kwargs:
        data = kwargs['data']
    else:
        data = ''
    if 'params' in kwargs:
        params = kwargs['params']
    else:
        params = ''

    html_response = session.get(url=url, params=params, data=data)
    if html_response.status_code == 200:
        return html_response.content
    else:
        print('Error with HTML GET of {}.  Status code {}.'.format(url, html_response.status_code))
        return False


def main():
    with requests.Session() as session:
        # Log in
        login_data = {'user_login': USERNAME, 'user_password': PASSWORD}
        session.post('{}/'.format(url), data=login_data,)

        # Grab the HTML for the pages we are going to parse.
        results_html = get_html_content(session=session,
                                        url='{}/results'.format(url),
                                        params='limit={}'.format(results_limit),
                                        )
        """
        account_html = get_html_content(session=session,
                                        url='{}/account/'.format(url),
                                        params='details=1',
                                        )
        cpus_html = get_html_content(session=session,
                                     url='{}/cpus/'.format(url),
                                     )
        top_500_html = get_html_content(session=session,
                                        url='{}/report_top_500/'.format(url),
                                        )
        """

        soup = bs(results_html, 'lxml')
        tabler = soup.find(id='report1')
        



if __name__ == '__main__':
    main()
