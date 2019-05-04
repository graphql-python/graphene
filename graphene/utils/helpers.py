from base64 import b64encode as _base64, b64decode as _unbase64


def base64(s):
    return _base64(s.encode('utf-8')).decode('utf-8')


def unbase64(s):
    return _unbase64(s).decode('utf-8')


def is_str(s):
    return isinstance(s, str)