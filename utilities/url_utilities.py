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
