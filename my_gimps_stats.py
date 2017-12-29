#!/usr/bin/python3
"""Query www.mersenne.org for stats on your GIMPS account."""

from userdata import *
from utilities import url_utilities, global_variiables
import requests


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
        session.post('{}/'.format(global_variiables.main_url), data=login_data, )

        # Grab the HTML for the pages we are going to parse.
        results_html = url_utilities.get_html_content(
            session=session,
            url='{}/results'.format(global_variiables.main_url),
            params='limit={}'.format(global_variiables.results_limit),
        )
        cpus_html = url_utilities.get_html_content(
            session=session,
            url='{}/cpus/'.format(global_variiables.main_url),
        )
        account_html = url_utilities.get_html_content(
            session=session,
            url='{}/account/'.format(global_variiables.main_url),
            params='details=1',
        )
        top_500_html = url_utilities.get_html_content(
            session=session,
            url='{}/report_top_500/'.format(global_variiables.main_url),
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

    # The def parse_table() doesn't handle the Account nor Top 500 web pages well.
    my_rank_365, my_overall_365, my_ghzdays_365 = url_utilities.get_account_stats('report1', account_html)
    my_rank_lifetime, my_overall_lifetime, my_ghzdays_lifetime = url_utilities.get_account_stats(
        'report2', account_html)

    # Collect the Top 500 table for comparison parsing vs. my stats.
    my_score = float(my_ghzdays_365.replace(',', ''))
    my_rank = int(float(my_rank_365.replace(',', '')))
    if my_rank > 500:
        next_rank = '500'
    else:
        next_rank = str(my_rank - 1)
    next_rank_ghzdays = float(url_utilities.get_500_level_stats(html_content=top_500_html, rank=next_rank))
    days2go = (next_rank_ghzdays - my_score) / daily_average

    print("Ave GHz-Days per day: {}".format(format(daily_average, '.4f')))
    print("Workers: {}".format(cpu_count))
    print("365 Rank: {}/{}".format(my_rank_365, my_overall_365))
    print("Lifetime Rank: {}/{}".format(my_rank_lifetime, my_overall_lifetime))
    print("Estimate reaching rank {} in {} days.".format(next_rank, format(days2go, '.1f')))


if __name__ == '__main__':
    main()
