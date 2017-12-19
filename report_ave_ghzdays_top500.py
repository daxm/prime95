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


def get_html_content(session, url, data='', params=''):
    """
    :param session: required, the requests session.
    :param url: required, the URL being queried.
    :param data: optional, based on FORM style POST/PUT actions.
    :param params: optional, based on variables passed as a part of the URL path (e.g. ?var1=1&var2=2)
    :return: response.content
    """

    html_response = session.get(url=url, params=params, data=data)
    if html_response.status_code == 200:
        return html_response.content
    else:
        print('Error with HTML GET of {}.  Status code {}.'.format(url, html_response.status_code))


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
                for i, ggchild in enumerate(gchild.children):  # This is the <td> level.
                    if i == 0:
                        rank = ggchild.text
                    elif i == 1:
                        member_name = ggchild.text
                    elif i == 2:
                        ghzdays = ggchild.text
                    else:
                        break
                line_entry = (str(gather_date), rank, member_name, ghzdays)
                rank_data.append(line_entry)
            except AttributeError:
                pass
    return rank_data


def main():
    with requests.Session() as session:
        # Grab the HTML for the pages we are going to parse.
        top_500_html = get_html_content(
            session=session,
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
            then_year, then_month, then_day = historical_row[0].split('-')
            date_then = datetime.date(int(then_year), int(then_month), int(then_day))
            date_delta = (date_today - date_then).days
            if date_delta > 0:
                ghzdays_delta = float(ghzdays) - float(historical_row[3])
                ghzdays_ave = ghzdays_delta / date_delta
                print('For rank {} the average ghzdays is {}.'.format(rank, format(ghzdays_ave, '.4f')))
            else:
                print('There is no new date data for rank {} thus no comparison can be made.'.format(rank))

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
