class TooManyArgs(Exception):
    pass


class TooFewArgs(Exception):
    pass


def either(expected):
    def inner(func):
        def wrapper(*args, **kwargs):

            arg_list = [kwargs.get(arg, None) is not None for arg in expected]

            if not any(arg_list):
                raise TooFewArgs("Too few arguments, must be either of: " + ",".join(expected))

            if arg_list.count(True) > 1:
                raise TooManyArgs("Too many arguments, must be either of: " + ",".join(expected))

            return func(*args, **kwargs)
        return wrapper
    return inner
