import inspect

from ..utils.props import props


class Options(object):
    '''
    This is the class wrapper around Meta.
    It helps to validate and cointain the attributes inside
    '''

    def __init__(self, meta=None, **defaults):
        if meta:
            assert inspect.isclass(meta), (
                'Meta have to be a class, received "{}".'.format(repr(meta))
            )

        meta_attrs = props(meta) if meta else {}
        for attr_name, value in defaults.items():
            if attr_name in meta_attrs:
                value = meta_attrs.pop(attr_name)
            setattr(self, attr_name, value)

        # If meta_attrs is not empty, it implicitly means
        # it received invalid attributes
        if meta_attrs:
            raise TypeError(
                "Invalid attributes: {}".format(
                    ', '.join(sorted(meta_attrs.keys()))
                )
            )

    def extend_with_defaults(self, defaults):
        for attr_name, value in defaults.items():
            if not hasattr(self, attr_name):
                setattr(self, attr_name, value)
        return self

    def __repr__(self):
        options_props = props(self)
        props_as_attrs = ' '.join(['{}={}'.format(key, value) for key, value in options_props.items()])
        return '<Options {}>'.format(props_as_attrs)
