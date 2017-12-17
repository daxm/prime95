#!/usr/bin/python3
"""Query www.mersenne.org for stats on your GIMPS account."""

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
                for ggchild in gchild.children:  # This is the <td> level.
                    if counter == 0:
                        rank = ggchild.text
                    elif counter == 1:
                        member_name = ggchild.text
                    elif counter == 2:
                        ghzdays = ggchild.text
                    else:
                        break
                    counter += 1
                line_entry = (str(gather_date), rank, member_name, ghzdays)
                rank_data.append(line_entry)
            except AttributeError:
                pass
    return rank_data


def main():
    with requests.Session() as session:
        # Grab the HTML for the pages we are going to parse.
        top_500_html = get_html_content(session=session,
                                        url='{}/report_top_500/'.format(main_url),
                                        )

    # Collect the Top 500 table for comparison parsing vs. my stats.
    today_data = get_top500_data(html_content=top_500_html)
    date_today = datetime.date.today()

    conn = sqlite3.connect('top_500.db')
    cursor = conn.cursor()

    for row in today_data:
        rank = row[1]
        ghzdays = row[3]
        cursor.execute("SELECT * from top500 WHERE rank = '{}'".format(rank))
        for historical_row in cursor:
            date_delta = 1  # FIXME.  Need to compute days between today and what is in top_500.db.
            if date_delta > 0:
                ghzdays_delta = float(ghzdays) - float(historical_row[3])
                ghzdays_ave = ghzdays_delta / date_delta
                print('For rank {} the average ghzdays is {}.'.format(rank, ghzdays_ave))
            else:
                print('There is no new date data for rank {} thus no comparison can be made.'.format(rank))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
