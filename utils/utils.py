import os
import platform
import datetime


def get_creation_date(path):
    if platform.system() == 'Windows':
        dt = datetime.datetime.fromtimestamp(os.path.getctime(path))
        date_str = str(dt.date())
        time_str = str(dt.time().strftime('%H%M%S'))
        return date_str, time_str
    else:
        # On Unix-like systems, getctime returns *last metadata change* time
        # So we try to use stat with birth_time if available
        stat = os.stat(path)
        try:
            dt = datetime.datetime.fromtimestamp(stat.st_birthtime)
            date_str = str(dt.date())
            time_str = str(dt.time().strftime('%H%M%S'))
            return date_str, time_str

        except AttributeError:
            # st_birthtime not available, fallback to last modified time
            dt = datetime.datetime.fromtimestamp(stat.st_mtime)
            date_str = str(dt.date())
            time_str = str(dt.time().strftime('%H%M%S'))
            return date_str, time_str

# Example
# file_path = '__init__.py'
# print(get_creation_date(file_path))
