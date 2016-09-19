import functools

import six

_INDENT = 4


def _wrap_in_new_lines(formatted_fields):
    return '\n{}\n'.format(formatted_fields) if formatted_fields else ''


def _wrap_fields_name(name, object_type, formatted_fields, indent_level):
    return '{}({}{})'.format(name, formatted_fields, ' ' * (indent_level * _INDENT))


def _wrap_fields_in_class_name(object_type, formatted_fields, indent_level):
    class_name = object_type.__class__.__name__
    return _wrap_fields_name(class_name, object_type, formatted_fields, indent_level)


def _wrap_fields_in_full_package_name(object_type, formatted_fields, indent_level):
    full_name = '{}.{}'.format(object_type.__module__, object_type.__class__.__name__)
    return _wrap_fields_name(full_name, object_type, formatted_fields, indent_level)


def _format_field_for_simple_type(field_value):
    if isinstance(field_value, six.string_types):
        return "'{}'".format(field_value)
    else:
        return field_value


def _get_formatted_field(field_name, field_value, indent_level, full_package_name):
    from ..types.objecttype import ObjectType
    if isinstance(field_value, ObjectType):
        formatted_field_value = object_type_to_string(field_value, indent_level + 1, full_package_name)
    else:
        formatted_field_value = _format_field_for_simple_type(field_value)

    field_definition = '{}={}'.format(field_name, formatted_field_value)
    spacing = len(field_definition) + (indent_level + 1) * _INDENT
    formatted_field = '{message:>{fill}}'.format(message=field_definition, fill=spacing)
    return formatted_field


def object_type_to_string(object_type, indent_level=0, full_package_name=False):
    get_existing_fields = (field_name for field_name in six.viewkeys(object_type._meta.fields) if
                           getattr(object_type, field_name, None))
    get_formatted_field_prepared = functools.partial(_get_formatted_field, indent_level=indent_level,
                                                     full_package_name=full_package_name)
    formatted_fields = ',\n'.join((get_formatted_field_prepared(field_name, getattr(object_type, field_name)) for
                                  field_name in get_existing_fields))
    formatted_fields = _wrap_in_new_lines(formatted_fields)

    if full_package_name:
        return _wrap_fields_in_full_package_name(object_type, formatted_fields, indent_level)
    else:
        return _wrap_fields_in_class_name(object_type, formatted_fields, indent_level)
