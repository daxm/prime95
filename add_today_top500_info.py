#!/usr/bin/python3
"""Query www.mersenne.org for stats on your GIMPS account."""

from userdata import *
import requests
from lxml import html
from bs4 import BeautifulSoup
import sqlite3
import datetime

# ### Possible changeable data ### #
main_url = 'https://www.mersenne.org'
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


def get_top500_data(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    tabler = soup.find(id='report1')
    rank_data = []
    rank = ''
    member_name = ''
    ghzdays = ''
    gather_date = datetime.date.today()

    for child in tabler.children:  # This is the <thead> and <tbody> level.
        if child.name != 'tbody':
            continue
        for gchild in child.children:  # This is the <tr> level.
            try:
                counter = 0
                for ggchild in gchild.children:
                    if counter == 1:
                        rank = ggchild.text
                    if counter == 2:
                        member_name = ggchild.text
                    if counter == 3:
                        ghzdays = ggchild.text
                    if counter > 3:
                        break
                    counter += 1
                line_entry = (str(gather_date), rank, member_name, ghzdays)
                rank_data.append(line_entry)
            except AttributeError:
                pass
    return rank_data


def main():
    with requests.Session() as session:
        # Log in
        login_data = {'user_login': USERNAME, 'user_password': PASSWORD}
        session.post('{}/'.format(main_url), data=login_data, )

        # Grab the HTML for the pages we are going to parse.
        top_500_html = get_html_content(session=session,
                                        url='{}/report_top_500/'.format(main_url),
                                        )

    conn = sqlite3.connect('top_500.db')
    cursor = conn.cursor()

    # Collect the Top 500 table for comparison parsing vs. my stats.
    today_data = get_top500_data(html_content=top_500_html)
    cursor.executemany('INSERT INTO top500 VALUES(?, ?, ?, ?)', today_data)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
