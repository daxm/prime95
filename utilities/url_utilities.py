from bs4 import BeautifulSoup
import datetime
from utilities import text_utilities
from lxml import html


def get_html_content(session, url, data='', params='',):
    """
    :param session: required, the requests session.
    :param url: required, the URL being queried.
    :param data: optional, based on FORM style POST/PUT actions.
    :param params: optional, based on variables passed as a part of the URL path (e.g. ?var1=1&var2=2)
    :return: response.content
    """
    html_response = session.get(url=url, params=params, data=data)
    if html_response.status_code == 200:
        return html_response.content
    else:
        print('Error with HTML GET of {}.  Status code {}.'.format(url, html_response.status_code))


def get_top500_data(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    tabler = soup.find(id='report1')
    rank_data = []
    rank = ''
    member_name = ''
    ghzdays = ''
    gather_date = datetime.date.today()

    for child in tabler.children:  # This is the <thead> and <tbody> level.
        if child.name != 'tbody':
            continue
        for gchild in child.children:  # This is the <tr> level.
            try:
                counter = 0
                for ggchild in gchild.children:
                    if counter == 0:
                        rank = ggchild.text
                    elif counter == 1:
                        member_name = ggchild.text
                    elif counter == 2:
                        ghzdays = ggchild.text
                    else:
                        break
                    counter += 1
                line_entry = (str(gather_date), rank, member_name, ghzdays)
                rank_data.append(line_entry)
            except AttributeError:
                pass
    return rank_data


def parse_table(table_id, html_content):
    """Using table_id parse the HTML content to get to table data."""

    tree = html.fromstring(html_content)
    data_set = []

    # I'm not fully sure what all this next block of code does but it certainly cleans up my data!
    # https://stackoverflow.com/questions/28305578/python-get-html-table-data-by-xpath
    for table in tree.xpath('//table[@id="{}"]'.format(table_id)):
        header = [text_utilities.text(th) for th in table.xpath('//th')]  # 1
        data_set = [[text_utilities.text(td) for td in tr.xpath('td')]
                    for tr in table.xpath('//tr')]  # 2
        data_set = [row for row in data_set if len(row) == len(header)]  # 3

    return data_set


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
                    for i, ggchild in enumerate(gchild.children):
                        if i == 2 and this_is_the_one:
                            this_is_the_one = False
                            ghzdays = ggchild.text
                    break
            except AttributeError:  # For some reason there is a extra BeautifulSoup
                pass
    return ghzdays


def get_account_stats(table_id, html_content):
    """This gleans the your rank values (for the last 365 days and overall) as well as your total earned ghz-days."""
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
                for i, ggchild in enumerate(gchild.children):
                    if i == 1:
                        my_rank = ggchild.text
                    elif i == 2:
                        my_overall = ggchild.text
                    elif i == 3:
                        my_ghzdays = ggchild.text
    return my_rank, my_overall, my_ghzdays
