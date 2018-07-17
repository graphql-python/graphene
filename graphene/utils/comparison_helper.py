def raise_assertion_if(condition=None, message=None):
    if condition:
        raise AssertionError(message)
