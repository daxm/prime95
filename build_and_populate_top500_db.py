#!/usr/bin/python3
"""Build and populate the top_500.db sqlite3 database with baseline data."""

import requests
import os
from utilities import url_utilities, db_utilities
from userdata import *

# ### Possible changeable data ### #
main_url = 'https://www.mersenne.org'
db_name = 'top_500.db'
# ### # 



def main():
    # db_directory is a OS path variable stored in userdata.py
    db = os.path.join(db_directory, db_name)
    if not os.path.isfile(db):
        db_utilities.create_db(db)

    # Populate the database with today's Top 500 data.
    with requests.Session() as session:
        # Grab the HTML for the pages we are going to parse.
        top_500_html = url_utilities.get_html_content(session=session, url='{}/report_top_500/'.format(main_url))

    today_data = url_utilities.get_top500_data(html_content=top_500_html)
    db_utilities.add_today_ranks(data=today_data, db_name=db)


if __name__ == '__main__':
    main()
