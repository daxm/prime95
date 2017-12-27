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
    date_year_ago = date_today - datetime.timedelta(days=365)

    conn = sqlite3.connect('top_500.db')
    cursor = conn.cursor()

    # Trying out plotting data on a graph.
    # Uncomment these lines to get a graphical plot of normalized data.
    # import plotly
    # from plotly.graph_objs import Scatter, Layout
    # plotx = []
    # ploty = []

    for row in today_data:
        rank = row[1]
        ghzdays = row[3]
        sql = "select * from top500 where (date_captured >= '{}' and date_captured <= '{}')" \
              "and rank = '{}' order by date_captured limit 1".format(date_year_ago, date_today, rank)
        cursor.execute(sql)

        for historical_row in cursor:
            then_year, then_month, then_day = historical_row[0].split('-')
            date_then = datetime.date(int(then_year), int(then_month), int(then_day))
            date_delta = (date_today - date_then).days
            if date_delta > 0:
                ghzdays_delta = float(ghzdays) - float(historical_row[3])
                ghzdays_ave = ghzdays_delta / date_delta
                print('For rank {} the average ghzdays is {}.'.format(rank, format(ghzdays_ave, '.4f')))
                # Uncomment these lines to get a graphical plot of normalized data.
                # plotx.append(rank)
                # ploty.append(ghzdays_ave / float(ghzdays))
            else:
                print('There is no new date data for rank {} thus no comparison can be made.'.format(rank))

    # Uncomment these lines to get a graphical plot of normalized data.
    # plotly.offline.plot({"data": [Scatter(x=plotx, y=ploty)], "layout": Layout(title="hello world.")})

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
