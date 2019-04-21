import dateparser


def try_dateparser(date, date_formats=None):
    return dateparser.parse(date, date_formats)
