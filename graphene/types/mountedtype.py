from ..utils.orderedtype import OrderedType
from .unmountedtype import UnmountedType


class MountedType(OrderedType):

    _mount_cls_override = None

    @classmethod
    def mounted(cls, unmounted):  # noqa: N802
        '''
        Mount the UnmountedType instance
        '''
        assert isinstance(unmounted, UnmountedType), (
            '{} can\'t mount {}'
        ).format(cls.__name__, repr(unmounted))

        mount_cls = cls._mount_cls_override or cls

        return mount_cls(
            unmounted.get_type(),
            *unmounted.args,
            _creation_counter=unmounted.creation_counter,
            **unmounted.kwargs
        )
