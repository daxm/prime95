#!/usr/bin/python3
"""Find average GHz-Days for recent work done on GIMPS.  http://www.mersenne.org"""

from userdata import *
import requests
from lxml import html

# ### Possible changeable data ### #
# results_limit can be anything from '1' to '9999'.
results_limit = '9999'
# Set account_details to 1 for expanded version or 0 for not.
account_details = '1'
# ### #


def text(elt):
    return elt.text_content().replace(u'\xa0', u' ')


def get_results(session, results_url, results_params):
    # Get and format needed data.
    response = session.get(results_url, params=results_params)
    tree = html.fromstring(response.content)

    # I'm not fully sure what all this next block of code does but it certainly cleans up my data!
    # https://stackoverflow.com/questions/28305578/python-get-html-table-data-by-xpath
    for table in tree.xpath('//table[@id="report1"]'):
        header = [text(th) for th in table.xpath('//th')]  # 1
        data_set = [[text(td) for td in tr.xpath('td')]
                   for tr in table.xpath('//tr')]  # 2
        data_set = [row for row in data_set if len(row) == len(header)]  # 3
        # data_set = pd.DataFrame(data_set, columns=header)  # 4 (I have no need to beautify the data_set at this time.)
    return data_set


def compute_ghzdays_average(data_set):
    """Return the sum of the average daily ghz-days for each entry in the data_set."""
    daily_average = 0
    for row in data_set:
        daily_average += (float(row[6]) / float(row[4]))
    return daily_average


def main():
    # Build URLs
    domain = 'www.mersenne.org'
    url = 'https://{}'.format(domain)
    main_url = url
    login_url = '{}/'.format(url)
    login_data = {'user_login': USERNAME, 'user_password': PASSWORD}
    results_url = '{}/results/'.format(url)
    results_params = 'limit={}'.format(results_limit)
    account_url = '{}/account/'.format(url)
    account_params = 'details={}'.format(account_details)

    with requests.Session() as session:
        # Log in
        session.post(login_url, data=login_data,)

        # Work with results page
        results_data = get_results(session, results_url, results_params)
        daily_average = compute_ghzdays_average(results_data)
        print("Daily average GHz-days on the given dataset is {}".format(daily_average))

if __name__ == '__main__':
    main()
