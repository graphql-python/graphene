def raise_assertion_if_true(condition=None, message=None):
	if condition:
		raise AssertionError(message)