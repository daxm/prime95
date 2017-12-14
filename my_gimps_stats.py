#!/usr/bin/python3
"""Query www.mersenne.org for stats on your GIMPS account."""

from userdata import *
import requests
from lxml import html
from bs4 import BeautifulSoup

# ### Possible changeable data ### #
main_url = 'https://www.mersenne.org'
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
        data_set = [row for row in data_set if len(row) == len(header)]  # 3

    return data_set


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


def get_500_level_stats(html_content, rank):
    soup = BeautifulSoup(html_content, 'lxml')
    tabler = soup.find(id='report1')
    this_is_the_one = False
    ghzdays = 0
    for child in tabler.children:  # This is the <thead> and <tbody> level.
        if child.name != 'tbody':
            continue
        for gchild in child.children:  # This is the <tr> level.
            try:
                for ggchild in gchild.children:  # this is the <td> level.
                    if ggchild.text != rank:
                        continue
                    this_is_the_one = True
                if this_is_the_one:
                    counter = 0
                    for ggchild in gchild.children:
                        if counter == 2 and this_is_the_one:
                            this_is_the_one = False
                            ghzdays = ggchild.text
                        counter += 1
                    break
            except AttributeError:  # For some reason there is a extra BeautifulSoup
                pass
    return ghzdays


def get_account_stats(table_id, html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    tabler = soup.find(id='{}'.format(table_id))
    this_is_the_one = False
    my_rank = 0
    my_overall = 0
    my_ghzdays = 0
    for child in tabler.children:  # This is the <thead> and <tbody> level.
        if child.name != 'tbody':
            continue
        for gchild in child.children:  # This is the <tr> level.
            for ggchild in gchild.children:  # this is the <td> level.
                if ggchild.text != 'Overall':
                    continue
                this_is_the_one = True
            if this_is_the_one:
                counter = 0
                for ggchild in gchild.children:
                    if counter == 1:
                        my_rank = ggchild.text
                    if counter == 2:
                        my_overall = ggchild.text
                    if counter == 3:
                        my_ghzdays = ggchild.text
                    counter += 1
    return my_rank, my_overall, my_ghzdays


def main():
    with requests.Session() as session:
        # Log in
        login_data = {'user_login': USERNAME, 'user_password': PASSWORD}
        session.post('{}/'.format(main_url), data=login_data, )

        # Grab the HTML for the pages we are going to parse.
        results_html = get_html_content(session=session,
                                        url='{}/results'.format(main_url),
                                        params='limit={}'.format(results_limit),
                                        )
        cpus_html = get_html_content(session=session,
                                     url='{}/cpus/'.format(main_url),
                                     )
        account_html = get_html_content(session=session,
                                        url='{}/account/'.format(main_url),
                                        params='details=1',
                                        )
        top_500_html = get_html_content(session=session,
                                        url='{}/report_top_500/'.format(main_url),
                                        )

    # Now grab table(s) that we need out of the HTML files grabbed.
    results_table = parse_table(table_id='report1', html_content=results_html)
    cpus_table = parse_table(table_id='report1', html_content=cpus_html)

    # Compute your daily average GHz-days per day.  On average this is how many GHz-days you should receive daily.
    daily_average = compute_ghzdays_average(results_table)
    # Find all the CPUs that have a GHz-day value.
    cpu_count = cpus_with_ghzdays(cpus_table)
    # Compute daily average GHz-days for CPUs that have reported in.
    daily_average = daily_average * cpu_count
    print("{} workers have reported in, giving a daily average GHz-days of {}."
          .format(cpu_count, format(daily_average, '.4f')))

    # The def parse_table() doesn't handle the Account nor Top 500 web pages well.
    my_rank_365, my_overall_365, my_ghzdays_365 = get_account_stats('report1', account_html)
    print('My last 365 day Rank: {}/{}'.format(my_rank_365, my_overall_365))
    my_rank_lifetime, my_overall_lifetime, my_ghzdays_lifetime = get_account_stats('report2', account_html)
    print('My Overall Rank: {}/{}'.format(my_rank_lifetime, my_overall_lifetime))

    # Collect the Top 500 table for comparison parsing vs. my stats.
    ghzdays_500 = int(float(get_500_level_stats(html_content=top_500_html, rank='500')) * 10000)
    my_score = int(float(my_ghzdays_lifetime.replace(',', '')) * 10000)
    days2go = 99999.9999
    if my_score < ghzdays_500:
        print('Your rank is smaller than 500.')
        delta = (ghzdays_500 - my_score) / 10000
        days2go = delta / daily_average
    else:
        ghzdays_250 = int(float(get_500_level_stats(html_content=top_500_html, rank='250')) * 10000)
        if my_score < ghzdays_250:
            print('Your rank is between 500 and 250.')
            delta = (ghzdays_250 - my_score) / 10000
            days2go = delta / daily_average
        else:
            ghzdays_125 = int(float(get_500_level_stats(html_content=top_500_html, rank='125')) * 10000)
            if my_score < ghzdays_125:
                print('Your rank is between 250 and 125.')
                delta = (ghzdays_125 - my_score) / 10000
                days2go = delta / daily_average
            else:
                ghzdays_100 = int(float(get_500_level_stats(html_content=top_500_html, rank='100')) * 10000)
                if my_score < ghzdays_100:
                    print('Your rank is between 125 and 100.')
                    delta = (ghzdays_100 - my_score) / 10000
                    days2go = delta / daily_average
                else:
                    ghzdays_50 = int(float(get_500_level_stats(html_content=top_500_html, rank='50')) * 10000)
                    if my_score < ghzdays_50:
                        print('Your rank is between 100 and 50.')
                        delta = (ghzdays_50 - my_score) / 10000
                        days2go = delta / daily_average
                    else:
                        ghzdays_25 = int(float(get_500_level_stats(html_content=top_500_html, rank='25')) * 10000)
                        if my_score < ghzdays_25:
                            print('Your rank is between 50 and 25.')
                            delta = (ghzdays_25 - my_score) / 10000
                            days2go = delta / daily_average
                        else:
                            ghzdays_10 = int(float(get_500_level_stats(html_content=top_500_html, rank='10')) * 10000)
                            if my_score < ghzdays_10:
                                print('Your rank is between 25 and 10.')
                                delta = (ghzdays_10 - my_score) / 10000
                                days2go = delta / daily_average
                            else:
                                ghzdays_1 = int(float(get_500_level_stats(html_content=top_500_html, rank='1')) * 10000)
                                if my_score < ghzdays_1:
                                    print('Your rank is between 10 and 1.')
                                    delta = (ghzdays_1 - my_score) / 10000
                                    days2go = delta / daily_average
                                else:
                                    print("You must have done something REALLY naughty.\
                                      You shouldn't see this output.")

    print('At this rate you should surpass this rank in {} days.'.format(format(days2go, '.1f')))
    print('NOTE:  Remember that they are probably increasing their "Total GHz Days" so the expected intersect day '
          'will probably be further out in the furture than this predicted date.  If you are not increasing your '
          'GHz Days as quickly as they are you will never reach them!')


if __name__ == '__main__':
    main()
