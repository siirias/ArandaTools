from datetime import datetime
import argparse
import warnings


# hard-coded header entries that must match exactly
target_header = {
    'Ship': 'ARANDA',
}


def short_warning_format(msg, *args, **kwargs):
    return str(msg) + '\n'


warnings.formatwarning = short_warning_format


def warn(condition, message):
    if not condition:
        warnings.warn(message)


def no_check(s):
    return True


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def has_no_whitespace(s):
    return len(s.split()) == 1


def is_fmi_date(d):
    try:
        datetime.strptime(d, '%d.%m.%Y %H.%M')
        return True
    except ValueError:
        return False


class MessageManager:
    """
    Decorator class to read header and generate warning message.
    """
    def __init__(self, func):
        self.func = func

    def __call__(self, key, header, *args, **kwargs):
        v = header[key]
        fn = header['filename']
        msg = f'{fn}: Could not parse "{key}": {v}'
        # pass value and message to decorated function
        self.func(v, msg, *args, **kwargs)


@MessageManager
def check_latlon(v, msg):
    warn(len(v.split()) == 2, msg)

    a, b = v.split()
    warn(a.isnumeric(), msg)
    warn(is_float(b), msg)


def check_kind(v, msg, kind_check, count=1, length=None):

    def _check(x):
        warn(kind_check(x), msg)

    if count > 1:
        warn(len(v.split(',')) == count, msg)
        for x in v.split(','):
            _check(x.strip())
    else:
        if length is not None:
            warn(len(v.strip()) == length, msg)
        _check(v)


@MessageManager
def check_float(v, msg, count=1, length=None):
    check_kind(v, msg, is_float, count=count, length=length)


@MessageManager
def check_integer(v, msg, count=1, length=None):
    check_kind(v, msg, is_int, count=count, length=length)


@MessageManager
def check_string(v, msg, count=1, length=None, alpha_only=False,
                 no_whitespace=False):
    kind_check = no_check
    if alpha_only:
        kind_check = str.isalpha
    if no_whitespace:
        kind_check = has_no_whitespace
    check_kind(v, msg, kind_check, count=count, length=length)


@MessageManager
def check_datetime(v, msg):
    warn(is_fmi_date(v), msg)


@MessageManager
def check_cruise(v, msg):
    words = v.split(',')
    warn(len(words) == 2, msg)
    cruise_number = words[0]
    warn(len(cruise_number.split('/')) == 2, msg)
    for x in cruise_number.split('/'):
        warn(x.isnumeric(), msg)


def check_cnv_header(cnvfile):
    """
    Check SeaBird cnv header for validity.

    Checks only manually entered header entries. Prints warnings of offending
    entries to stdout.

    :arg cnvfile: cnv filename to process
    """
    header = {}
    with open(cnvfile, 'r', encoding="latin-1") as cf:
        for line in cf.readlines():
            # parse lines that begin with '**'
            if line[:2] != '**':
                continue
            key, value = line.strip().split(':', 1)
            key = key.replace('**', '').strip()
            value = value.strip()
            header[key] = value
    # store filename in header dict
    header['filename'] = cnvfile
    for key in target_header:
        msg = f'Bad entry: "{key}"\n "{header[key]}" != "{target_header[key]}"'
        warn(header[key] == target_header[key], msg)
    # parse entries
    check_integer('Index', header, length=4)
    check_cruise('Cruise (# , name)', header)
    check_latlon('Latitude', header)
    check_latlon('Longitude', header)
    check_datetime('Date and time (UTC)', header)
    check_integer('Depth', header)
    check_string('CTD operator , Winch operator', header, count=2,
                 alpha_only=True, no_whitespace=True)
    check_float('Wind speed, Direction, Pressure', header, count=3)
    check_float('Sea temperature, Air temperature', header, count=2)
    check_integer('Secchi depth', header)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Check validity of SBE cnv file headers')
    parser.add_argument('files', metavar='cnv_file', nargs='+',
                        help='*.cnv files to process')
    args = parser.parse_args()

    for f in args.files:
        check_cnv_header(f)
