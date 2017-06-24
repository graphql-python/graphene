import re


def to_camel_case(snake_str):
    """
    Return a camel-cased version of a snake-cased string.

    Leading underscores and multiple-underscores are kept
    intact.

    :param snake_str: A snake-cased string.
    :return: A camel-cased string.
    """
    # Find all subcomponents in a snake-cased string, including
    # any trailing underscores, which are treated as a separate
    # component.
    snake_case_sub_strings = re.findall(r'(_*[a-zA-Z]+|_+$)', snake_str)

    # The first variable is unchanged case wise (and leading
    # underscores preserved as-is).
    camel_case_sub_strings = [snake_case_sub_strings[0]]

    for s in snake_case_sub_strings[1:]:
        # We reset the camel casing algorithm if more than one
        # underscore is encountered.  The endwiths handles any
        # trailing underscores in the original snake-cased
        # variable.
        if s.startswith('__') or s.endswith('_'):
            camel_case_sub_strings.append(s)
            continue

        # Otherwise we replace '_name' with 'Name', for example.
        camel_case_sub_strings.append(s[1:].title())

    return ''.join(camel_case_sub_strings)


# From this response in Stackoverflow
# http://stackoverflow.com/a/1176023/1072990
def to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_const(string):
    return re.sub('[\W|^]+', '_', string).upper()
