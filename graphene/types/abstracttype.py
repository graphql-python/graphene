from ..utils.subclass_with_meta import SubclassWithMeta
from ..utils.deprecated import warn_deprecation


class AbstractType(SubclassWithMeta):

    def __init_subclass__(cls, *args, **kwargs):
        warn_deprecation(
            "Abstract type is deprecated, please use normal object inheritance instead.\n"
            "See more: https://github.com/graphql-python/graphene/blob/2.0/UPGRADE-v2.0.md#deprecations"
        )
        super(AbstractType, cls).__init_subclass__(*args, **kwargs)
