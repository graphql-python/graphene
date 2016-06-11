from ..utils.props import props


class Options(object):
    '''
    This is the class wrapper around Meta.
    It helps to validate and cointain the attributes inside
    '''

    def __init__(self, meta=None, **defaults):
        self.add_attrs_from_meta(meta, defaults)

    def add_attrs_from_meta(self, meta, defaults):
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
