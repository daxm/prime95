#!/usr/bin/python3
"""Query www.mersenne.org for stats on your GIMPS account."""

from userdata import *
import requests
from lxml import html

# ### Possible changeable data ### #
url = 'https://www.mersenne.org'
# results_limit can be anything from '1' to '9999'.
results_limit = '9999'
# ### #


def text(elt):
    return elt.text_content().replace(u'\xa0', u' ')


def parse_table(table_id, html_content):
    """Using table_id parse the HTML content to get to table data."""

    tree = html.fromstring(html_content)
    data_set = []

    # I'm not fully sure what all this next block of code does but it certainly cleans up my data!
    # https://stackoverflow.com/questions/28305578/python-get-html-table-data-by-xpath
    for table in tree.xpath('//table[@id="{}"]'.format(table_id)):
        # header = [text(th) for th in table.xpath('//th')]  # 1
        data_set = [[text(td) for td in tr.xpath('td')]
                    for tr in table.xpath('//tr')]  # 2
        """Some of my "data_set" HTML tables are formatted in a way that gets messed up by # 3 so I'm
         going to deal with the data_set inline in the code instead of here."""
        # data_set = [row for row in data_set if len(row) == len(header)]  # 3

    return data_set


def cpus_with_ghzdays(data_set):
    """Return the number of rows with GHz Days value > 0 and Status == 'T'."""

    count = 0
    for row in data_set:
        if row[5] == ' T' and row[6] != '0.0':
            count += 1

    return count


def get_rankings(rank_table):
    """Parse the 'account data' to find your rankings out of total."""

    your_rank = ''
    all_ranks = ''
    print(rank_table)

    return your_rank, all_ranks


def compute_ghzdays_average(data_set):
    """Return the sum of the average daily ghz-days for each entry in the data_set."""

    daily_average = 0
    count = 0
    for row in data_set:
        daily_average += (float(row[6]) / float(row[4]))
        count += 1

    # Average GHz-days per day for all entries.
    daily_average = daily_average / count

    return daily_average


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

    # Now grab table(s) that we need out of the HTML files grabbed.
    results_table = parse_table(table_id='report1', html_content=results_html)
    results_table = [row for row in results_table if row != []]
    cpus_table = parse_table(table_id='report1', html_content=cpus_html)
    cpus_table = [row for row in cpus_table if row != []]

    account_365_table = parse_table(table_id='report1', html_content=account_html)
    account_365_table = [row for row in account_365_table if len(row) == 5]
    print(account_365_table)
    account_overall_table = parse_table(table_id='report2', html_content=account_html)
    top_500_table = parse_table(table_id='report1', html_content=top_500_html)

    # Compute your daily average GHz-days per day.  On average this is how many GHz-days you should receive daily.
    daily_average = compute_ghzdays_average(results_table)
    # Find all the CPUs that have a GHz-day value.
    cpu_count = cpus_with_ghzdays(cpus_table)
    # Compute daily average GHz-days for CPUs that have reported in.
    daily_average = daily_average * cpu_count
    print("{} workers have reported in, giving a daily average GHz-days of {}."
          .format(cpu_count, format(daily_average, '.4f')))

    """
    # Compute days until in Top 500
    get_top_500(session)

    # Work with account page to get rankings
    year_table, lifetime_table = get_account(session)
    year_rank, year_outof = get_rankings(rank_table=year_table)
    print("Of the last year rank:{}/{}".format(year_rank, year_outof))
    lifetime_rank, lifetime_outof = get_rankings(rank_table=lifetime_table)
    print("Lifetime rank:{}/{}".format(lifetime_rank, lifetime_outof))
    """


if __name__ == '__main__':
    main()
