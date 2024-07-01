from typing import Type, Optional

from ..utils.subclass_with_meta import SubclassWithMeta, SubclassWithMeta_Meta
from ..utils.trim_docstring import trim_docstring


class BaseOptions:
    name: Optional[str] = None
    description: Optional[str] = None

    _frozen: bool = False

    def __init__(self, class_type: Type):
        self.class_type: Type = class_type

    def freeze(self):
        self._frozen = True

    def __setattr__(self, name, value):
        if not self._frozen:
            super(BaseOptions, self).__setattr__(name, value)
        else:
            raise Exception(f"Can't modify frozen Options {self}")

    def __repr__(self):
        return f"<{self.__class__.__name__} name={repr(self.name)}>"


BaseTypeMeta = SubclassWithMeta_Meta


class BaseType(SubclassWithMeta):
    @classmethod
    def create_type(cls, class_name, **options):
        return type(class_name, (cls,), {"Meta": options})

    @classmethod
    def __init_subclass_with_meta__(
        cls, name=None, description=None, _meta=None, **_kwargs
    ):
        assert "_meta" not in cls.__dict__, "Can't assign meta directly"
        if not _meta:
            return
        _meta.name = name or cls.__name__
        _meta.description = description or trim_docstring(cls.__doc__)
        _meta.freeze()
        cls._meta = _meta
        super(BaseType, cls).__init_subclass_with_meta__()
