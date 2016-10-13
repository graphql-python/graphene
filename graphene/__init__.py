from .pyutils.version import get_version


try:
    # This variable is injected in the __builtins__ by the build
    # process. It used to enable importing subpackages when
    # the required packages are not installed
    __SETUP__
except NameError:
    __SETUP__ = False


VERSION = (1, 0, 2, 'final', 0)

__version__ = get_version(VERSION)

if not __SETUP__:

    from .types import (
        AbstractType,
        ObjectType,
        InputObjectType,
        Interface,
        Mutation,
        Field,
        InputField,
        Schema,
        Scalar,
        String, ID, Int, Float, Boolean,
        List, NonNull,
        Enum,
        Argument,
        Dynamic,
        Union,
    )
    from .relay import (
        Node,
        is_node,
        GlobalID,
        ClientIDMutation,
        Connection,
        ConnectionField,
        PageInfo
    )
    from .utils.resolve_only_args import resolve_only_args

    __all__ = [
        'AbstractType',
        'ObjectType',
        'InputObjectType',
        'Interface',
        'Mutation',
        'Field',
        'InputField',
        'Schema',
        'Scalar',
        'String',
        'ID',
        'Int',
        'Float',
        'Enum',
        'Boolean',
        'List',
        'NonNull',
        'Argument',
        'Dynamic',
        'Union',
        'resolve_only_args',
        'Node',
        'is_node',
        'GlobalID',
        'ClientIDMutation',
        'Connection',
        'ConnectionField',
        'PageInfo']
