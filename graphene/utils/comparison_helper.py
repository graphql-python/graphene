def raise_assertion_if_not(condition=None, message=None):
    if not condition:
        raise AssertionError(message)
