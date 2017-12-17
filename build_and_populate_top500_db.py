#!/usr/bin/python3
"""Build and populate the top_500.db sqlite3 database with baseline data."""

import requests
from lxml import html
from bs4 import BeautifulSoup
import sqlite3
import datetime
import os

# ### Possible changeable data ### #
main_url = 'https://www.mersenne.org'
db_name = 'top_500.db'
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
    # Create the database.
    conn = sqlite3.connect(db_name)

    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE top500
                    (date_captured text, rank text, ghzdays real, member_name text,
                    UNIQUE (date_captured, rank) ON CONFLICT IGNORE)''')
    conn.commit()
    conn.close()

    # Populate the database with today's Top 500 data.
    with requests.Session() as session:
        # Grab the HTML for the pages we are going to parse.
        top_500_html = get_html_content(session=session,
                                        url='{}/report_top_500/'.format(main_url),
                                        )

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Collect the Top 500 table for comparison parsing vs. my stats.
    today_data = get_top500_data(html_content=top_500_html)
    cursor.executemany('INSERT INTO top500 VALUES(?, ?, ?, ?)', today_data)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    if os.path.exists(db_name):
        print('It appears you already have a {} file.  Delete/Move that file and run this script again.  '
              'Skipping creation and population of {}.'.format(db_name, db_name))
    else:
        main()
