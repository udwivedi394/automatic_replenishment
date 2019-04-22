import datetime

import dateparser


def try_dateparser(date, date_formats=None):
    return dateparser.parse(date, date_formats)


def try_timestamp_combinations(timestamp_string, datetime_format_array):
    for datetime_format in datetime_format_array:
        try:
            timestamp = datetime.datetime.strptime(timestamp_string, datetime_format)
            return timestamp
        except Exception as e:
            # print(e)
            pass
    raise ValueError('Unable to retrieve timestamp!')
