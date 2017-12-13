#!/usr/bin/python3
"""Find average GHz-Days for recent work done on GIMPS.  http://www.mersenne.org"""

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
        header = [text(th) for th in table.xpath('//th')]  # 1
        data_set = [[text(td) for td in tr.xpath('td')]
                    for tr in table.xpath('//tr')]  # 2
        print('{}/{}'.format(len(data_set[1]),len(header)))
        data_set = [row for row in data_set if len(row) == len(header)]  # 3

    return data_set


def get_results(session):
    """Grab the data from the /results URL and parse out into data_set."""

    results_url = '{}/results/'.format(url)
    results_params = 'limit={}'.format(results_limit)

    # Get and format needed data.
    response = session.get(results_url, params=results_params)
    data_set = parse_table(table_id='report1', html_content=response.content)

    return data_set


def get_cpus(session):
    """Grab the data from the /cpus URL and parse out into data_set."""

    # Get and format needed data.
    response = session.get('{}/cpus/'.format(url))
    data_set = parse_table(table_id='report1', html_content=response.content)

    return data_set


def cpus_with_ghzdays(data_set):
    """Return the number of rows with GHz Days value > 0 and Status == 'T'."""

    count = 0
    for row in data_set:
        if row[5] == ' T' and row[6] != '0.0':
            count+=1

    return count


def get_account(session):
    """Grab the data from the /account URL and parse out into data_set."""

    account_url = '{}/account/'.format(url)
    account_params = 'details=1'

    # Get and format needed data.
    response = session.get(account_url, params=account_params)

    year_table = parse_table(table_id='report1', html_content=response.content)
    lifetime_table = parse_table(table_id='report2', html_content=response.content)
    print(year_table)

    return year_table, lifetime_table


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
        count+=1

    # Average GHz-days per day for all entries.
    daily_average = daily_average / count

    return daily_average


def get_top_500(session):
    """Grab the data from the /report_top_500 URL and parse out into data_set."""

    # Get and format needed data.
    response = session.get('{}/report_top_500/'.format(url))
    data_set = parse_table(table_id='report1', html_content=response.content)
    return data_set


def main():
    login_url = '{}/'.format(url)
    login_data = {'user_login': USERNAME, 'user_password': PASSWORD}

    with requests.Session() as session:
        # Log in
        session.post(login_url, data=login_data,)

        # Work with results page
        results_data = get_results(session)
        daily_average = compute_ghzdays_average(results_data)
        # Find all the CPUs that have a GHz-day value.
        results_cpus = get_cpus(session)
        cpu_count = cpus_with_ghzdays(results_cpus)
        # Compute daily average GHz-days for CPUs that have reported in.
        daily_average = daily_average * cpu_count
        print("{} workers have reported in giving a daily average GHz-days of {}.".format(cpu_count,
                                                                                         format(daily_average, '.4f')))

        # Compute days until in Top 500
        get_top_500(session)

        """
        # Work with account page to get rankings
        year_table, lifetime_table = get_account(session)
        year_rank, year_outof = get_rankings(rank_table=year_table)
        print("Of the last year rank:{}/{}".format(year_rank, year_outof))
        lifetime_rank, lifetime_outof = get_rankings(rank_table=lifetime_table)
        print("Lifetime rank:{}/{}".format(lifetime_rank, lifetime_outof))
        """


if __name__ == '__main__':
    main()
