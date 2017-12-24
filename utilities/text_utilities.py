def text(elt):
    return elt.text_content().replace(u'\xa0', u' ')
