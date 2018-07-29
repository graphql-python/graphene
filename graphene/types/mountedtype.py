from ..utils.orderedtype import OrderedType
from .unmountedtype import UnmountedType
from ..utils.comparison_helper import raise_assertion_if_not


class MountedType(OrderedType):
    @classmethod
    def mounted(cls, unmounted):  # noqa: N802
        """
        Mount the UnmountedType instance
        """
        raise_assertion_if_not(
            condition=isinstance(unmounted, UnmountedType),
            message="{} can't mount {}".format(cls.__name__, repr(unmounted))
        )

        return cls(
            unmounted.get_type(),
            *unmounted.args,
            _creation_counter=unmounted.creation_counter,
            **unmounted.kwargs
        )
