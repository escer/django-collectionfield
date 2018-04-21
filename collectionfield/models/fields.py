# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models.fields import Field
from django.core import exceptions
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.utils import six

from collectionfield.converter import CollectionConverter
from collectionfield.validators import (
    ConvertedMaxLengthValidator, MaxItemsValidator
)
from collectionfield import forms as cf_forms
from .lookups import Has, HasAll, HasAny


def create_get_field_display(field):
    """
    Creates `get_FIELD_display` model method for CollectionField with choices
    :param field: a CollectionField instance
    :return: function
    """

    def default_mapper(value, label):
        return label

    def default_wrapper(field_display):
        return field_display

    def get_field_display(obj, delimiter=", ", mapper=None, wrapper=None):
        """
        Renders current field value as string with possibility to
        override the behavior using extra params:
        :param obj: current model instance
        :param delimiter: string used to join the selected options
        :param mapper: function to map value and label into string
                       that represents single item of the collection
                       (outputs label by default),
        :param wrapper: function that maps joined selected options into final
                        string representation (does nothing by default).
        :return: string representation of selected choices
        """
        mapper = mapper or default_mapper
        wrapper = wrapper or default_wrapper
        selected_values = getattr(obj, field.attname)
        if hasattr(field, 'flatchoices'):  # Django 1.9
            value_to_label = dict(field.flatchoices)
        else:
            value_to_label = dict(field.get_flatchoices())
        labels = []
        for single_value in selected_values:
            single_label = value_to_label[single_value]
            labels.append(mapper(single_value, single_label))
        field_display = delimiter.join(labels)
        return wrapper(field_display)

    return get_field_display


class CollectionField(Field):
    """Model field to store collections"""

    def __init__(self, verbose_name=None, name=None, collection_type=list,
                 item_type=six.text_type, sort=False, unique_items=None,
                 max_items=None, delimiter='|', **kwargs):
        """
        :param collection_type: type (class) of this collection
        :param item_type: type (class) of this collection's items
        :param sort: should items be sorted automatically?
        :param unique_items: should duplicate items be dropped?
        :param max_items: maximum number of items (enforced on validation)
        :param delimiter: separates items in string representation stored in db
        :param max_length: maximum length string representation
                           of this collection
        """
        self.collection_type = collection_type
        self.item_type = item_type
        self.sort = sort
        self.unique_items = unique_items
        self.max_items = max_items
        self.delimiter = delimiter
        kwargs['max_length'] = kwargs.get('max_length', 1024)
        kwargs['default'] = kwargs.get('default', self.collection_type)
        empty_collection = collection_type()
        if empty_collection not in self.empty_values:
            self.empty_values = self.empty_values[:] + [empty_collection]
        super(CollectionField, self).__init__(
            verbose_name=verbose_name, name=name, **kwargs
        )
        if self.max_items:
            self.validators.append(MaxItemsValidator(self.max_items))
        self.validators.append(
            ConvertedMaxLengthValidator(
                limit_value=self.max_length,
                collection_type=self.collection_type,
                item_type=self.item_type,
                sort=self.sort,
                unique_items=self._has_unique_items(),
                delimiter=self.delimiter
            )
        )

    def deconstruct(self):
        name, path, args, kwargs = super(CollectionField, self).deconstruct()
        if self.collection_type is not list:
            kwargs['collection_type'] = self.collection_type
        if self.item_type is not six.text_type:
            kwargs['item_type'] = self.item_type
        if self.sort:
            kwargs['sort'] = True
        if self.unique_items is not None:
            kwargs['unique_items'] = self.unique_items
        if self.max_items is not None:
            kwargs['max_items'] = self.max_items
        if self.delimiter != '|':
            kwargs['delimiter'] = self.delimiter
        if kwargs.get('max_length') == 1024:
            del kwargs['max_length']
        if kwargs.get('default') is self.collection_type:
            del kwargs['default']
        return name, path, args, kwargs

    def get_internal_type(self):
        return 'CharField'

    def from_db_value(self, value, expression, connection, context):
        return self.collection_converter.load(value)

    def to_python(self, value):
        if isinstance(value, self.collection_type):
            return value
        else:
            return self.collection_converter.load(value)

    def get_prep_value(self, value):
        return self.collection_converter.dump(value)

    def value_to_string(self, obj):
        """
        Returns a string value of this field from the passed obj.
        This is used by the serialization framework.
        """
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def validate(self, value, model_instance):
        """
        Validates value and throws ValidationError.
        Copied to fix builtin validation of choices.
        """
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self.choices and value not in self.empty_values:
            selected_choices = set(value)
            for option_key, option_value in self.choices:
                if isinstance(option_value, (list, tuple)):
                    # This is an optgroup, so look inside the group for
                    # options.
                    for optgroup_key, optgroup_value in option_value:
                        if optgroup_key in selected_choices:
                            selected_choices.remove(optgroup_key)
                elif option_key in selected_choices:
                    selected_choices.remove(option_key)
            if selected_choices:
                raise exceptions.ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': list(selected_choices)[0]},
                )

        if value is None and not self.null:
            raise exceptions.ValidationError(
                self.error_messages['null'], code='null'
            )

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(
                self.error_messages['blank'], code='blank'
            )

    def formfield(self, **kwargs):
        """Form field instance for this model field"""
        if self.choices:
            form_class = (
                kwargs.pop('choices_form_class', None) or
                cf_forms.CollectionChoiceField
            )
        else:
            form_class = (
                kwargs.pop('form_class', None) or cf_forms.CollectionField
            )

        if getattr(form_class, 'collection_field_compatible', False):
            defaults = {
                'required': not self.blank,
                'label': capfirst(self.verbose_name),
                'help_text': self.help_text,
                # CollectionField-specific params:
                'collection_type': self.collection_type,
                'item_type': self.item_type,
                'sort': self.sort,
                'unique_items': self._has_unique_items(),
                'max_items': self.max_items,
                'max_length': self.max_length,
            }
            if self.has_default():
                if callable(self.default):
                    defaults['initial'] = self.default
                    defaults['show_hidden_initial'] = True
                else:
                    defaults['initial'] = self.get_default()
            if self.choices:
                defaults['choices'] = self.get_choices(include_blank=False)
            defaults.update(kwargs)
            return form_class(**defaults)
        else:
            return super(CollectionField, self).formfield(**kwargs)

    def contribute_to_class(self, cls, name, **kwargs):
        """Overrides `get_FIELD_display` on model class"""
        super(CollectionField, self).contribute_to_class(
            cls, name, **kwargs
        )
        if self.choices:
            setattr(
                cls, 'get_{0}_display'.format(name),
                create_get_field_display(self)
            )

    # Custom methods:

    def _has_unique_items(self):
        return bool(self.unique_items) if not self.choices else True

    @cached_property
    def collection_converter(self):
        return CollectionConverter(
            collection_type=self.collection_type,
            item_type=self.item_type,
            sort=self.sort,
            unique_items=self._has_unique_items(),
            delimiter=self.delimiter
        )


# Register field lookups:
CollectionField.register_lookup(Has)
CollectionField.register_lookup(HasAll)
CollectionField.register_lookup(HasAny)
