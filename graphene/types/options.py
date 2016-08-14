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
            elif hasattr(meta, attr_name):
                value = getattr(meta, attr_name)
            setattr(self, attr_name, value)

        # If meta_attrs is not empty, it implicit means
        # it received invalid attributes
        if meta_attrs:
            raise TypeError(
                "Invalid attributes: {}".format(
                    ','.join(meta_attrs.keys())
                )
            )

    def __repr__(self):
        return '<Meta \n{} >'.format(props(self))
