#!/usr/bin/python3
"""Query www.mersenne.org for stats on your GIMPS account."""

import requests
import sqlite3
import datetime
from utilities import url_utilities, global_variiables


def main():
    with requests.Session() as session:
        # Grab the HTML for the pages we are going to parse.
        top_500_html = url_utilities.get_html_content(
            session=session,
            url='{}/report_top_500/'.format(global_variiables.main_url),
        )

    # Collect the Top 500 table for comparison parsing vs. my stats.
    today_data = url_utilities.get_top500_data(html_content=top_500_html)
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
