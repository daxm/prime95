#!/usr/bin/python3
"""Query www.mersenne.org for stats on your GIMPS account."""

from userdata import *
from utilities import url_utilities
import requests

# ### Possible changeable data ### #
main_url = 'https://www.mersenne.org'
# results_limit can be anything from '1' to '9999'.
results_limit = '9999'
# ### #


def cpus_with_ghzdays(data_set):
    """Return the number of rows with GHz Days value > 0 and Status == 'T'."""

    count = 0
    for row in data_set:
        if row[5] == ' T' and row[6] != '0.0':
            count += 1

    return count


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


def main():
    with requests.Session() as session:
        # Log in
        login_data = {'user_login': USERNAME, 'user_password': PASSWORD}
        session.post('{}/'.format(main_url), data=login_data, )

        # Grab the HTML for the pages we are going to parse.
        results_html = url_utilities.get_html_content(
            session=session,
            url='{}/results'.format(main_url),
            params='limit={}'.format(results_limit),
        )
        cpus_html = url_utilities.get_html_content(
            session=session,
            url='{}/cpus/'.format(main_url),
        )
        account_html = url_utilities.get_html_content(
            session=session,
            url='{}/account/'.format(main_url),
            params='details=1',
        )
        top_500_html = url_utilities.get_html_content(
            session=session,
            url='{}/report_top_500/'.format(main_url),
        )

    # Now grab table(s) that we need out of the HTML files grabbed.
    results_table = url_utilities.parse_table(table_id='report1', html_content=results_html)
    cpus_table = url_utilities.parse_table(table_id='report1', html_content=cpus_html)

    # Compute your daily average GHz-days per day.  On average this is how many GHz-days you should receive daily.
    daily_average = compute_ghzdays_average(results_table)
    # Find all the CPUs that have a GHz-day value.
    cpu_count = cpus_with_ghzdays(cpus_table)
    # Compute daily average GHz-days for CPUs that have reported in.
    daily_average = daily_average * cpu_count
    print("{} workers have reported in, giving a daily average GHz-days of {}."
          .format(cpu_count, format(daily_average, '.4f')))

    # The def parse_table() doesn't handle the Account nor Top 500 web pages well.
    my_rank_365, my_overall_365, my_ghzdays_365 = url_utilities.get_account_stats('report1', account_html)
    print('Your last 365 day Rank: {} out of {} active reports.'.format(my_rank_365, my_overall_365))
    my_rank_lifetime, my_overall_lifetime, my_ghzdays_lifetime = url_utilities.get_account_stats(
        'report2', account_html)
    print('Your Overall Lifetime Rank: {} out of {} reported.'.format(my_rank_lifetime, my_overall_lifetime))

    # Collect the Top 500 table for comparison parsing vs. my stats.
    my_score = float(my_ghzdays_365.replace(',', ''))
    my_rank = int(float(my_overall_365.replace(',', '')))
    if my_rank > 500:
        next_rank = '500'
    else:
        next_rank = str(my_rank - 1)
    next_rank_ghzdays = float(url_utilities.get_500_level_stats(html_content=top_500_html, rank=next_rank))
    days2go = (next_rank_ghzdays - my_score) / daily_average
    print('At this rate you should surpass the next Top 500 '
          'rank, {}, in {} days.'.format(next_rank, format(days2go, '.1f')))
    print("""
#################################################################################
NOTE:  Remember that they are increasing their "Total GHz Days" too.
The expected intersect date will probably be further out than this predicted date.
#################################################################################
""")


if __name__ == '__main__':
    main()
