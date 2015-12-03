import binascii

from django.core.exceptions import ValidationError
from django.forms import Field, IntegerField, CharField
from django.utils.translation import ugettext_lazy as _

from graphql_relay import from_global_id


class GlobalIDFormField(Field):
    default_error_messages = {
        'invalid': _('Invalid ID specified.'),
    }

    def clean(self, value):
        if not value and not self.required:
            return None

        try:
            gid = from_global_id(value)
        except (UnicodeDecodeError, TypeError, binascii.Error):
            raise ValidationError(self.error_messages['invalid'])

        try:
            IntegerField().clean(gid.id)
            CharField().clean(gid.type)
        except ValidationError:
            raise ValidationError(self.error_messages['invalid'])

        return value
