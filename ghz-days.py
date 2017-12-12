#!/usr/bin/python3
"""Find average GHz-Days for recent work done on GIMPS.  http://www.mersenne.org"""

from userdata import *
import requests
from lxml import html

# ### Possible changeable data ### #
# results_limit can be anything from '1' to '9999'.
results_limit = '2'
# Set account_details to 1 for expanded version or 0 for not.
account_details = '1'
# ### #


def text(elt):
    return elt.text_content().replace(u'\xa0', u' ')


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

    # Get and format needed data.
    result = session.get(results_url, params='limit={}'.format(results_limit))
    tree = html.fromstring(result.content)
    # I'm not fully sure what all this next block of code does but it certainly cleans up my dataset!
    # https://stackoverflow.com/questions/28305578/python-get-html-table-data-by-xpath
    for table in tree.xpath('//table[@id="report1"]'):
        header = [text(th) for th in table.xpath('//th')]  # 1
        data = [[text(td) for td in tr.xpath('td')]
                for tr in table.xpath('//tr')]  # 2
        data = [row for row in data if len(row) == len(header)]  # 3
        # data = pd.DataFrame(data, columns=header)  # 4
        print(data)
