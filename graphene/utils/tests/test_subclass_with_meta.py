from ..subclass_with_meta import SubclassWithMeta


def test_init_subclass_calls_super():
    class DefinesInitSubclass:
        subclass_init_count = 0

        def __init_subclass__(cls, **kwargs):
            DefinesInitSubclass.subclass_init_count += 1
            super().__init_subclass__(**kwargs)

    class InheritsAsFirst(SubclassWithMeta, DefinesInitSubclass):
        pass

    class InheritsAsLast(DefinesInitSubclass, SubclassWithMeta):
        pass

    assert DefinesInitSubclass.subclass_init_count == 2


def test_kwargs_are_consumed():
    class DefinesInitSubclass:
        passed_kwargs = []

        def __init_subclass__(cls, **kwargs):
            if kwargs:
                DefinesInitSubclass.passed_kwargs.append(kwargs)
            super().__init_subclass__(**kwargs)

    class InheritsAsFirst(SubclassWithMeta, DefinesInitSubclass, is_consumed="foo"):
        pass

    class InheritsAsLast(DefinesInitSubclass, SubclassWithMeta, not_consumed="bar"):
        pass

    assert DefinesInitSubclass.passed_kwargs == [{"not_consumed": "bar"}]


def test_meta_is_deleted_and_props_passed():
    class DefinesInitSubclassWithMeta(SubclassWithMeta):
        passed_meta_options = []

        @classmethod
        def __init_subclass_with_meta__(cls, **options):
            if options:
                DefinesInitSubclassWithMeta.passed_meta_options.append(options)
            super().__init_subclass_with_meta__()

    class HasMetaClass(DefinesInitSubclassWithMeta, foo1=1):
        class Meta:
            foo2 = 2
            foo3 = 3

    class HasMetaDict(DefinesInitSubclassWithMeta, bar1=1):
        Meta = {"bar2": 2, "bar3": 3}

    assert not hasattr(HasMetaClass, "Meta")
    assert not hasattr(HasMetaDict, "Meta")

    assert DefinesInitSubclassWithMeta.passed_meta_options == [
        {"foo1": 1, "foo2": 2, "foo3": 3},
        {"bar1": 1, "bar2": 2, "bar3": 3},
    ]
