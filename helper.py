import datetime

def converted_to_string(time_string):
    if isinstance(time_string, datetime.date):
        time_string = time_string.strftime('%H%M')
    return time_string