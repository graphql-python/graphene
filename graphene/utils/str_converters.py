import re


# Adapted from this response in Stackoverflow
# http://stackoverflow.com/a/19053800/1072990
def to_camel_case(snake_str):

	# We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    def _camel_case_convert(components):
        return components[0] + "".join(x.capitalize() if x else "_" for x in components[1:])

    leading_underscore = False
    if snake_str.startswith('_'):
        leading_underscore = True
        snake_str = snake_str[1:]

    components = snake_str.split("_")

    if leading_underscore:
        return "_" + _camel_case_convert(components)
    return _camel_case_convert(components)


# From this response in Stackoverflow
# http://stackoverflow.com/a/1176023/1072990
def to_snake_case(name):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
