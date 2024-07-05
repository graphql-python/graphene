import re


# Adapted from this response in Stackoverflow
# http://stackoverflow.com/a/19053800/1072990
def to_camel_case(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    return components[0] + "".join(x.capitalize() if x else "_" for x in components[1:])


def to_snake_case(name):
    if not name:
        return name
    # Replace every capitalized letter (except the first one) by its lower case variant with an underscore before.
    return (name[0] + re.sub("([A-Z])", r"_\1", name[1:])).lower()
