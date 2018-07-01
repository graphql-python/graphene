from collections import defaultdict, Mapping, OrderedDict


def nested_dict():
    return defaultdict(nested_dict)


def deflate(node, index=None, path=None):
    if index is None:
        index = {}
    if path is None:
        path = []

    if node and 'id' in node and '__typename' in node:
        route = ','.join(path)

        if (
            route in index and
            node['__typename'] in index[route] and
            index[route][node['__typename']].get(node['id'])
        ):
            return {
                '__typename': node['__typename'],
                'id': node['id'],
            }
        else:
            if route not in index:
                index[route] = {}

            if node['__typename'] not in index[route]:
                index[route][node['__typename']] = {}

            index[route][node['__typename']][node['id']] = True

    field_names = node.keys()
    result = OrderedDict()

    for field_name in field_names:
        value = node[field_name]

        new_path = path + [field_name]
        if isinstance(value, (list, tuple)):
            result[field_name] = [
                deflate(child, index, new_path) for child in value
            ]
        elif isinstance(value, Mapping):
            result[field_name] = deflate(value, index, new_path)
        else:
            result[field_name] = value

    return result
