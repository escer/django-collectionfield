# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
from decimal import Decimal

import django
from django.utils import six
from django.core.exceptions import ValidationError
from django.core.serializers import serialize, deserialize
from django.forms import modelform_factory

from django.test import TestCase

from collectionfield.forms import CollectionField, CollectionChoiceField
from .models import (
    StringListModel, DefaultStringListModel, ChoiceStringListModel,
    SortedUniqueStringListModel, OptionalRangedIntegerListModel,
    DecimalSetModel, DefaultDecimalSetModel, SortedDecimalListModel,
    IntegerTupleModel, DefaultIntegerTupleModel, OptionalIntegerTupleModel,
    Max10CharsStringListModel, Max5ItemsStringListModel,
    OptionalGroupedChoiceStringListModel, OptionalGroupedChoiceIntegerListModel
)
from .forms import (
    StringSetForm, OptionalStringSetForm, IntegerListForm, DecimalTupleForm,
    SortedStringListForm, UniqueStringListForm, SpaceSeparatedIntegerListForm,
    Max3StringSetForm, Max10CharsStringListForm,
    ChoiceStringListForm, GroupedChoiceStringListForm,
    ChoiceIntegerSetForm, GroupedChoiceIntegerSetForm,
    ChoiceDecimalTupleForm, GroupedChoiceDecimalTupleForm,
    ChoiceMax2StringSetForm, ChoiceSortedIntegerListForm,
    ChoiceOptionalDecimalSetForm,
)


DJANGO_110 = django.VERSION >= (1, 10)


class ModelSaveTestCase(TestCase):

    def test_save_choice_string_list_model(self):
        ChoiceStringListModel.objects.create(
            values=['aaa', 'ccc']
        )
        obj = ChoiceStringListModel.objects.get()
        self.assertEqual(obj.values, ['aaa', 'ccc'])

    def test_save_sorted_unique_string_list_model(self):
        SortedUniqueStringListModel.objects.create(
            values=['Lightsabers', 'Aliens', 'Starships', 'Aliens']
        )
        obj = SortedUniqueStringListModel.objects.get()
        self.assertEqual(
            obj.values, ['Aliens', 'Lightsabers', 'Starships']
        )

    def test_save_optional_ranged_integer_list_model(self):
        OptionalRangedIntegerListModel.objects.create(
            values=[5, 4, 5, 2, 2, 5, 3]
        )
        obj = OptionalRangedIntegerListModel.objects.get()
        self.assertEqual(
            obj.values, [5, 4, 5, 2, 2, 5, 3]
        )

    def test_save_blank_optional_ranged_integer_list_model(self):
        OptionalRangedIntegerListModel.objects.create()
        obj = OptionalRangedIntegerListModel.objects.get()
        self.assertEqual(obj.values, [])

    def test_save_empty_optional_ranged_integer_list_model(self):
        OptionalRangedIntegerListModel.objects.create(values=[])
        obj = OptionalRangedIntegerListModel.objects.get()
        self.assertEqual(obj.values, [])

    def test_save_sorted_decimal_list_model(self):
        SortedDecimalListModel.objects.create(
            values=(
                Decimal('2.5'), Decimal('1.0'), Decimal('3.5'), Decimal('1.0')
            )
        )
        obj = SortedDecimalListModel.objects.get()
        self.assertEqual(
            obj.values,
            [Decimal('1.0'), Decimal('1.0'), Decimal('2.5'),  Decimal('3.5')]
        )

    def test_save_optional_integer_tuple_model(self):
        OptionalIntegerTupleModel.objects.create(
            values=(9, 0, 2, 0, 1)
        )
        obj = OptionalIntegerTupleModel.objects.get()
        self.assertEqual(
            obj.values, (9, 0, 2, 0, 1)
        )

    def test_save_blank_optional_integer_tuple_model(self):
        OptionalIntegerTupleModel.objects.create()
        obj = OptionalIntegerTupleModel.objects.get()
        self.assertEqual(obj.values, ())

    def test_save_empty_optional_integer_tuple_model(self):
        OptionalIntegerTupleModel.objects.create(values=())
        obj = OptionalIntegerTupleModel.objects.get()
        self.assertEqual(obj.values, ())

    def test_save_default_string_list_model(self):
        DefaultStringListModel.objects.create(values=['Test'])
        obj = DefaultStringListModel.objects.get()
        self.assertEqual(obj.values, ['Test'])

    def test_save_blank_default_string_list_model(self):
        DefaultStringListModel.objects.create()
        obj = DefaultStringListModel.objects.get()
        self.assertEqual(obj.values, ['Default', 'Values'])

    def test_save_default_decimal_set_model(self):
        DefaultDecimalSetModel.objects.create(values={Decimal('22.33')})
        obj = DefaultDecimalSetModel.objects.get()
        self.assertEqual(obj.values, {Decimal('22.33')})

    def test_save_blank_default_decimal_set_model(self):
        DefaultDecimalSetModel.objects.create()
        obj = DefaultDecimalSetModel.objects.get()
        self.assertEqual(obj.values, {Decimal('0.0')})

    def test_save_default_integer_tuple_model(self):
        DefaultIntegerTupleModel.objects.create(values=(22, 33))
        obj = DefaultIntegerTupleModel.objects.get()
        self.assertEqual(obj.values, (22, 33))

    def test_save_blank_default_integer_tuple_model(self):
        DefaultIntegerTupleModel.objects.create()
        obj = DefaultIntegerTupleModel.objects.get()
        self.assertEqual(obj.values, (-1,))

    def test_save_string_list_model_using_set(self):
        StringListModel.objects.create(values={'A', 'B'})
        obj = StringListModel.objects.get()
        self.assertIsInstance(obj.values, list)
        self.assertEqual(set(obj.values), {'A', 'B'})

    def test_save_decimal_set_model_using_tuple(self):
        DecimalSetModel.objects.create(
            values=(Decimal('11.5'), Decimal('1.0'))
        )
        obj = DecimalSetModel.objects.get()
        self.assertEqual(obj.values, {Decimal('11.5'), Decimal('1.0')})

    def test_save_integer_tuple_model_using_list(self):
        IntegerTupleModel.objects.create(values=[13, 99])
        obj = IntegerTupleModel.objects.get()
        self.assertEqual(obj.values, (13, 99))


class HasLookupTestCase(TestCase):

    def test_retrieve_existing_text(self):
        obj1 = StringListModel.objects.create(
            values=['Aliens', 'Starships', 'Aliens']
        )
        obj2 = StringListModel.objects.create(
            values=['Lions', 'Jungle']
        )
        obj3 = StringListModel.objects.create(
            values=['Pyramids', 'Aliens', 'Lions']
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__has='Aliens')),
            [obj1, obj3]
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__has='Jungle')),
            [obj2]
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__has='Knights')),
            []
        )

    def test_empty_results_on_partial_text_match(self):
        StringListModel.objects.create(
            values=['Aliens', 'Starships', 'Aliens']
        )
        StringListModel.objects.create(
            values=['Lions', 'Jungle']
        )
        StringListModel.objects.create(
            values=['Pyramids', 'Aliens', 'Lions']
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__has='Alien')),
            []
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__has='Pyramid')),
            []
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__has='Starship')),
            []
        )

    def test_retrieve_existing_int(self):
        obj1 = IntegerTupleModel.objects.create(
            values=(9, 0, 2, 0, 1)
        )
        obj2 = IntegerTupleModel.objects.create(
            values=(4, 3, 0, 2)
        )
        obj3 = IntegerTupleModel.objects.create(
            values=(9, 0, 2, 0, 1, 5)
        )
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__has=0)),
            [obj1, obj2, obj3]
        )
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__has=9)),
            [obj1, obj3]
        )
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__has=7)),
            []
        )

    def test_retrieve_existing_decimal(self):
        obj1 = DecimalSetModel.objects.create(
            values={Decimal('2.5'), Decimal('1.0'), Decimal('3.5')}
        )
        obj2 = DecimalSetModel.objects.create(
            values={Decimal('3.0'), Decimal('3.5'), Decimal('1.0')}
        )
        obj3 = DecimalSetModel.objects.create(
            values={Decimal('5.9'), Decimal('1.0'), Decimal('0.0')}
        )
        self.assertListEqual(
            list(DecimalSetModel.objects.filter(values__has=Decimal('1.0'))),
            [obj1, obj2, obj3]
        )
        self.assertListEqual(
            list(DecimalSetModel.objects.filter(values__has=Decimal('3.5'))),
            [obj1, obj2]
        )
        self.assertListEqual(
            list(DecimalSetModel.objects.filter(values__has=Decimal('9.9'))),
            []
        )


class HasAllLookupTestCase(TestCase):

    def test_has_all_texts(self):
        obj1 = StringListModel.objects.create(
            values=['Aliens', 'Starships', 'Aliens']
        )
        obj2 = StringListModel.objects.create(
            values=['Lions', 'Jungle']
        )
        obj3 = StringListModel.objects.create(
            values=['Pyramids', 'Aliens', 'Lions']
        )
        obj4 = StringListModel.objects.create(
            values=['Lions', 'Jungle', 'Monkeys']
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__hasall=['Aliens'])),
            [obj1, obj3]
        )
        self.assertListEqual(
            list(
                StringListModel.objects.filter(
                    values__hasall=['Jungle', 'Starships']
                )
            ),
            []
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__hasall=['Knights'])),
            []
        )
        self.assertListEqual(
            list(
                StringListModel.objects.filter(
                    values__hasall=['Lions', 'Jungle']
                )
            ),
            [obj2, obj4]
        )

    def test_has_all_integers(self):
        obj1 = IntegerTupleModel.objects.create(values=(9, 0, 2, 0, 1))
        obj2 = IntegerTupleModel.objects.create(values=(4, 3, 0, 2))
        obj3 = IntegerTupleModel.objects.create(values=(9, 0, 2, 0, 1, 5))
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__hasall=[0])),
            [obj1, obj2, obj3]
        )
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__hasall=[9, 4])),
            []
        )
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__hasall=[2, 9])),
            [obj1, obj3]
        )

    def test_has_all_decimals(self):
        DecimalSetModel.objects.create(
            values={Decimal('2.5'), Decimal('1.0'), Decimal('3.5')}
        )
        DecimalSetModel.objects.create(
            values={Decimal('3.0'), Decimal('3.5'), Decimal('1.0')}
        )
        obj3 = DecimalSetModel.objects.create(
            values={Decimal('5.9'), Decimal('1.0'), Decimal('0.0')}
        )
        obj4 = DecimalSetModel.objects.create(
            values={Decimal('0.0'), Decimal('1.0')}
        )
        self.assertListEqual(
            list(
                DecimalSetModel.objects.filter(
                    values__hasall=[Decimal('1.0'), Decimal('0.0')]
                )
            ),
            [obj3, obj4]
        )
        self.assertListEqual(
            list(
                DecimalSetModel.objects.filter(
                    values__hasall=[Decimal('3.5'), Decimal('0.0')]
                )
            ),
            []
        )
        self.assertListEqual(
            list(
                DecimalSetModel.objects.filter(
                    values__hasall=[Decimal('9.9')]
                )
            ),
            []
        )


class HasAnyLookupTestCase(TestCase):

    def test_has_any_texts(self):
        obj1 = StringListModel.objects.create(
            values=['Aliens', 'Starships', 'Aliens']
        )
        obj2 = StringListModel.objects.create(
            values=['Lions', 'Jungle']
        )
        obj3 = StringListModel.objects.create(
            values=['Pyramids', 'Aliens', 'Lions']
        )
        obj4 = StringListModel.objects.create(
            values=['Lions', 'Jungle', 'Monkeys']
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__hasany=['Aliens'])),
            [obj1, obj3]
        )
        self.assertListEqual(
            list(
                StringListModel.objects.filter(
                    values__hasany=['Jungle', 'Starships']
                )
            ),
            [obj1, obj2, obj4]
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values__hasany=['Knights'])),
            []
        )
        self.assertListEqual(
            list(
                StringListModel.objects.filter(
                    values__hasany=['Lions', 'Jungle']
                )
            ),
            [obj2, obj3, obj4]
        )

    def test_has_any_integers(self):
        obj1 = IntegerTupleModel.objects.create(values=(9, 0, 2, 0, 1))
        obj2 = IntegerTupleModel.objects.create(values=(4, 3, 0, 2))
        obj3 = IntegerTupleModel.objects.create(values=(9, 0, 2, 0, 1, 5))
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__hasany=[0])),
            [obj1, obj2, obj3]
        )
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__hasany=[5, 4])),
            [obj2, obj3]
        )
        self.assertListEqual(
            list(IntegerTupleModel.objects.filter(values__hasany=[7, 3])),
            [obj2]
        )

    def test_has_any_decimals(self):
        obj1 = DecimalSetModel.objects.create(
            values={Decimal('2.5'), Decimal('1.0'), Decimal('3.5')}
        )
        obj2 = DecimalSetModel.objects.create(
            values={Decimal('3.0'), Decimal('3.5'), Decimal('1.0')}
        )
        obj3 = DecimalSetModel.objects.create(
            values={Decimal('5.9'), Decimal('1.0'), Decimal('0.0')}
        )
        obj4 = DecimalSetModel.objects.create(
            values={Decimal('0.0'), Decimal('1.0')}
        )
        self.assertListEqual(
            list(
                DecimalSetModel.objects.filter(
                    values__hasany=[Decimal('1.0'), Decimal('0.0')]
                )
            ),
            [obj1, obj2, obj3, obj4]
        )
        self.assertListEqual(
            list(
                DecimalSetModel.objects.filter(
                    values__hasany=[Decimal('7.7'), Decimal('0.0')]
                )
            ),
            [obj3, obj4]
        )
        self.assertListEqual(
            list(
                DecimalSetModel.objects.filter(
                    values__hasany=[Decimal('9.9')]
                )
            ),
            []
        )


class OtherQueriesTestCase(TestCase):

    def test_full_match(self):
        StringListModel.objects.create(
            values=['Aliens', 'Starships', 'Aliens']
        )
        obj2 = StringListModel.objects.create(
            values=['Lions', 'Jungle']
        )
        StringListModel.objects.create(
            values=['Pyramids', 'Aliens', 'Lions']
        )
        obj4 = StringListModel.objects.create(
            values=['Lions', 'Jungle', 'Monkeys']
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values=['Aliens'])),
            []
        )
        self.assertListEqual(
            list(StringListModel.objects.filter(values=['Lions', 'Jungle'])),
            [obj2]
        )
        self.assertListEqual(
            list(
                StringListModel.objects.filter(
                    values=['Lions', 'Jungle', 'Monkeys']
                )
            ),
            [obj4]
        )


class GetFieldDisplayTestCase(TestCase):

    def test_get_field_display_text_default(self):
        obj1 = OptionalGroupedChoiceStringListModel.objects.create(
            values=['a1', 'b2']
        )
        obj2 = OptionalGroupedChoiceStringListModel.objects.create(
            values=['a2']
        )
        obj3 = OptionalGroupedChoiceStringListModel.objects.create(
            values=[]
        )
        self.assertEqual(obj1.get_values_display(), "A1, B2")
        self.assertEqual(obj2.get_values_display(), "A2")
        self.assertEqual(obj3.get_values_display(), "")

    def test_get_field_display_text_custom(self):

        def li_mapper(value, label):
            return "<li>{0}</li>".format(label)

        def ul_wrapper(field_display):
            return "<ul>{0}</ul>".format(field_display)

        obj1 = OptionalGroupedChoiceStringListModel.objects.create(
            values=['a1', 'b2']
        )
        obj2 = OptionalGroupedChoiceStringListModel.objects.create(
            values=['a2']
        )
        obj3 = OptionalGroupedChoiceStringListModel.objects.create(
            values=[]
        )
        self.assertEqual(
            obj1.get_values_display(
                delimiter="", mapper=li_mapper, wrapper=ul_wrapper
            ),
            "<ul><li>A1</li><li>B2</li></ul>"
        )
        self.assertEqual(
            obj2.get_values_display(
                delimiter="", mapper=li_mapper, wrapper=ul_wrapper
            ),
            "<ul><li>A2</li></ul>"
        )
        self.assertEqual(
            obj3.get_values_display(
                delimiter="", mapper=li_mapper, wrapper=ul_wrapper
            ),
            "<ul></ul>"
        )

    def test_get_field_display_int_default(self):
        obj1 = OptionalGroupedChoiceIntegerListModel.objects.create(
            values=[11, 22]
        )
        obj2 = OptionalGroupedChoiceIntegerListModel.objects.create(
            values=[12]
        )
        obj3 = OptionalGroupedChoiceIntegerListModel.objects.create(
            values=[]
        )
        self.assertEqual(obj1.get_values_display(), "1-1, 2-2")
        self.assertEqual(obj2.get_values_display(), "1-2")
        self.assertEqual(obj3.get_values_display(), "")

    def test_get_field_display_int_custom(self):

        def li_mapper(value, label):
            return "<li>{0}</li>".format(label)

        def ul_wrapper(field_display):
            return "<ul>{0}</ul>".format(field_display)

        obj1 = OptionalGroupedChoiceIntegerListModel.objects.create(
            values=[11, 22]
        )
        obj2 = OptionalGroupedChoiceIntegerListModel.objects.create(
            values=[12]
        )
        obj3 = OptionalGroupedChoiceIntegerListModel.objects.create(
            values=[]
        )
        self.assertEqual(
            obj1.get_values_display(
                delimiter="", mapper=li_mapper, wrapper=ul_wrapper
            ),
            "<ul><li>1-1</li><li>2-2</li></ul>"
        )
        self.assertEqual(
            obj2.get_values_display(
                delimiter="", mapper=li_mapper, wrapper=ul_wrapper
            ),
            "<ul><li>1-2</li></ul>"
        )
        self.assertEqual(
            obj3.get_values_display(
                delimiter="", mapper=li_mapper, wrapper=ul_wrapper
            ),
            "<ul></ul>"
        )


class ModelValidationTestCase(TestCase):

    def test_converted_max_length(self):
        obj1 = Max10CharsStringListModel(values=['The', 'End'])
        try:
            obj1.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexectedly.")
        obj2 = Max10CharsStringListModel(values=['The', 'End', 'Is', 'Near'])
        with self.assertRaises(ValidationError) as cm:
            obj2.full_clean()
        self.assertEqual(
            cm.exception.error_dict['values'][0].code, 'max_length'
        )

    def test_flat_choices(self):
        obj1 = ChoiceStringListModel(values=['aaa', 'ccc'])
        try:
            obj1.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexectedly.")
        obj2 = ChoiceStringListModel(values=['aaa', 'XXX'])
        with self.assertRaises(ValidationError) as cm:
            obj2.full_clean()
        self.assertEqual(
            cm.exception.error_dict['values'][0].code, 'invalid_choice'
        )

    def test_grouped_choices(self):
        obj1 = OptionalGroupedChoiceIntegerListModel(values=[11, 21, 22])
        try:
            obj1.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexectedly.")
        obj2 = OptionalGroupedChoiceIntegerListModel(values=[11, 21, 99])
        with self.assertRaises(ValidationError) as cm:
            obj2.full_clean()
        self.assertEqual(
            cm.exception.error_dict['values'][0].code, 'invalid_choice'
        )

    def test_blank(self):
        obj1 = OptionalIntegerTupleModel()
        try:
            obj1.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexectedly.")
        obj2 = IntegerTupleModel()
        with self.assertRaises(ValidationError) as cm:
            obj2.full_clean()
        self.assertEqual(
            cm.exception.error_dict['values'][0].code, 'blank'
        )

    def test_item_validators(self):
        obj1 = OptionalRangedIntegerListModel(values=[2, 4])
        try:
            obj1.full_clean()
        except ValidationError:
            self.fail("full_clean() raised ValidationError unexectedly.")
        obj2 = OptionalRangedIntegerListModel(values=[0, 9])
        with self.assertRaises(ValidationError) as cm:
            obj2.full_clean()
        self.assertEqual(
            cm.exception.error_dict['values'][0].code, 'min_value'
        )
        self.assertEqual(
            cm.exception.error_dict['values'][1].code, 'max_value'
        )


class DeconstructTestCase(TestCase):

    def test_string_list_field(self):
        field = StringListModel._meta.get_field('values')
        self.assertEqual(field.deconstruct()[3], {})

    def test_optional_integer_tuple_field(self):
        field = IntegerTupleModel._meta.get_field('values')
        self.assertEqual(
            field.deconstruct()[3],
            {
                'item_type': int,
                'collection_type': tuple
            }
        )

    def test_grouped_choice_integer_set_field(self):
        field = OptionalGroupedChoiceStringListModel._meta.get_field('values')
        self.assertEqual(
            field.deconstruct()[3],
            {
                'blank': True,
                'choices': [
                    ('Group A', (('a1', 'A1'), ('a2', 'A2'))),
                    ('Group B', (('b1', 'B1'), ('b2', 'B2')))
                ]
             }
        )


class ModelSerializationTestCase(TestCase):

    def test_model_serialization_json(self):
        obj = IntegerTupleModel.objects.create(values=(3, 1, 2))
        self.assertEqual(
            json.loads(serialize('json', [obj])),
            json.loads(
                '[{'
                '"fields": {"values": "|3|1|2|"}, '
                '"model": "tests.integertuplemodel", "pk": 1'
                '}]'
            )
        )

    def test_model_deserialization_json(self):
        dump = (
            '[{'
            '"fields": {"values": "|3|1|2|"}, '
            '"model": "tests.integertuplemodel", "pk": 1'
            '}]'
        )
        obj = list(deserialize('json', dump))[0].object
        self.assertEqual(obj.values, (3, 1, 2))


class FormCollectionFieldTestCase(TestCase):

    def test_valid_set_of_strings(self):
        form = StringSetForm({'values': "One, two, three"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], {"One", "two", "three"})

    def test_invalid_empty_set_of_strings(self):
        form = StringSetForm({'values': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_empty_set_of_strings_v2(self):
        form = StringSetForm({'values': ',, , '})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_valid_blank_set_of_strings(self):
        form = OptionalStringSetForm({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], set())

    def test_valid_list_of_integers(self):
        form = IntegerListForm({'values': "1,1,-9,0,77"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], [1, 1, -9, 0, 77])

    def test_invalid_empty_list_of_integers(self):
        form = IntegerListForm({'values': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_empty_list_of_integers_v2(self):
        form = IntegerListForm({'values': ',, , '})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_malformed_list_of_integers(self):
        form = IntegerListForm({'values': '1,2,XXX'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'invalid')

    def test_valid_tuple_of_decimals(self):
        form = DecimalTupleForm({'values': "2.33,-4.0,5"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'],
            (Decimal('2.33'), Decimal('-4.0'), Decimal('5'))
        )

    def test_invalid_empty_tuple_of_decimals(self):
        form = DecimalTupleForm({'values': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_empty_tuple_of_decimals_v2(self):
        form = DecimalTupleForm({'values': ',, , '})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_malformed_tuple_of_decimals(self):
        form = DecimalTupleForm({'values': '1.0, 2.5, XXX'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'invalid')

    def test_valid_sorted_list_of_strings(self):
        form = SortedStringListForm({'values': "b52,aaa,  z, aaa"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], ['aaa', 'aaa', 'b52', 'z']
        )

    def test_invalid_empty_sorted_list_of_strings(self):
        form = SortedStringListForm({'values': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_empty_sorted_list_of_strings_v2(self):
        form = SortedStringListForm({'values': ',, , '})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_valid_unique_list_of_strings(self):
        form = UniqueStringListForm({'values': "b52,aaa,  z, aaa"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], ['b52', 'aaa', 'z']
        )

    def test_invalid_empty_unique_list_of_strings(self):
        form = UniqueStringListForm({'values': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_empty_unique_list_of_strings_v2(self):
        form = UniqueStringListForm({'values': ',, , '})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_valid_space_separated_list_of_integers(self):
        form = SpaceSeparatedIntegerListForm({'values': "1 1 -9 0   77"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], [1, 1, -9, 0, 77])

    def test_invalid_empty_space_separated_list_of_integers(self):
        form = SpaceSeparatedIntegerListForm({'values': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_empty_space_separated_list_of_integers_v2(self):
        form = SpaceSeparatedIntegerListForm({'values': '      '})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_malformed_space_separated_list_of_integers(self):
        form = SpaceSeparatedIntegerListForm({'values': '1 2 XXX'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'invalid')

    def test_valid_set_of_up_to_3_strings(self):
        form = Max3StringSetForm({'values': "b52,aaa,  z, aaa"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], {'b52', 'aaa', 'z'}
        )

    def test_invalid_too_long_set_of_up_to_3_strings(self):
        form = Max3StringSetForm({'values': 'a, b, c, d'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'max_items')

    def test_invalid_empty_set_of_up_to_3_strings(self):
        form = Max3StringSetForm({'values': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_invalid_empty_set_of_up_to_3_strings_v2(self):
        form = Max3StringSetForm({'values': ',, , '})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'required')

    def test_max_length_exceeded(self):
        form = Max10CharsStringListForm({
            'values': ['a', 'b', 'c', 'd', 'e']  # 11 chars after conversion
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()['values'][0].code, 'max_length')

    def test_html_widget_without_value(self):
        bound_field = StringSetForm()['values']
        self.assertEqual(
            bound_field.as_widget(),
            '<input id="id_values" name="values" type="text"{req} />'.format(
                req=' required' if DJANGO_110 else ''
            )
        )

    def test_html_widget_with_value(self):
        bound_field = SortedStringListForm({'values': 'a, b, c'})['values']
        self.assertEqual(
            bound_field.as_widget(),
            '<input id="id_values" name="values" type="text" '
            'value="a, b, c"{req} />'.format(
                req=' required' if DJANGO_110 else ''
            )
        )


class FormCollectionChoiceFieldTestCase(TestCase):

    # Choice String List Form:

    def test_valid_choice_list_of_strings(self):
        form = ChoiceStringListForm({'values': ['a', 'b', 'd']})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], ['a', 'b', 'd'])

    def test_invalid_choice_list_of_strings(self):
        form = ChoiceStringListForm({'values': ['a', 'x', 'd']})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_choice'
        )

    def test_invalid_empty_choice_list_of_strings(self):
        form = ChoiceStringListForm({'values': []})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_blank_choice_list_of_strings(self):
        form = ChoiceStringListForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_type_choice_list_of_strings(self):
        form = ChoiceStringListForm({'values': 'abc'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_list'
        )

    # Grouped Choice String List Form:

    def test_valid_grouped_choice_list_of_strings(self):
        form = GroupedChoiceStringListForm({'values': ['a-1', 'b-2']})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], ['a-1', 'b-2'])

    def test_invalid_grouped_choice_list_of_strings(self):
        form = GroupedChoiceStringListForm({'values': ['a-1', 'b-9']})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_choice'
        )

    def test_invalid_empty_grouped_choice_list_of_strings(self):
        form = GroupedChoiceStringListForm({'values': []})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_blank_grouped_choice_list_of_strings(self):
        form = GroupedChoiceStringListForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_type_grouped_choice_list_of_strings(self):
        form = GroupedChoiceStringListForm({'values': 'a-2'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_list'
        )

    # Choice Integer Set Form:

    def test_valid_choice_set_of_integers(self):
        form = ChoiceIntegerSetForm({'values': [1, 3]})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], {1, 3})

    def test_invalid_choice_set_of_integers(self):
        form = ChoiceIntegerSetForm({'values': [1, 3, 9]})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_choice'
        )

    def test_invalid_empty_choice_set_of_integers(self):
        form = ChoiceIntegerSetForm({'values': []})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_blank_choice_set_of_integers(self):
        form = ChoiceIntegerSetForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_type_choice_set_of_integers(self):
        form = ChoiceIntegerSetForm({'values': '123'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_list'
        )

    # Grouped Choice Integer Set Form:

    def test_valid_grouped_choice_set_of_integers(self):
        form = GroupedChoiceIntegerSetForm({'values': [12, 21]})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], {12, 21})

    def test_invalid_grouped_choice_set_of_integers(self):
        form = GroupedChoiceIntegerSetForm({'values': [12, 21, 33]})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_choice'
        )

    def test_invalid_empty_grouped_choice_set_of_integers(self):
        form = GroupedChoiceIntegerSetForm({'values': []})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_blank_grouped_choice_set_of_integers(self):
        form = GroupedChoiceIntegerSetForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_type_grouped_choice_set_of_integers(self):
        form = GroupedChoiceIntegerSetForm({'values': '22'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_list'
        )

    # Choice Decimal Tuple Form:

    def test_valid_choice_tuple_of_decimals(self):
        form = ChoiceDecimalTupleForm({
            'values': [Decimal('1.5'), Decimal('2.5')]
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], (Decimal('1.5'), Decimal('2.5'))
        )

    def test_invalid_choice_tuple_of_decimals(self):
        form = ChoiceDecimalTupleForm({
            'values': [Decimal('1.5'), Decimal('3.3')]
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_choice'
        )

    def test_invalid_empty_choice_tuple_of_decimals(self):
        form = ChoiceDecimalTupleForm({'values': []})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_blank_choice_tuple_of_decimals(self):
        form = ChoiceDecimalTupleForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_type_choice_tuple_of_decimals(self):
        form = ChoiceDecimalTupleForm({'values': '1.5'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_list'
        )

    # Grouped Choice Decimal Tuple Form:

    def test_valid_grouped_choice_tuple_of_decimals(self):
        form = GroupedChoiceDecimalTupleForm({
            'values': [Decimal('1.1'), Decimal('2.2')]
        })
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], (Decimal('1.1'), Decimal('2.2'))
        )

    def test_invalid_grouped_choice_tuple_of_decimals(self):
        form = GroupedChoiceDecimalTupleForm({
            'values': [Decimal('1.1'), Decimal('3.3')]
        })
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_choice'
        )

    def test_invalid_empty_grouped_choice_tuple_of_decimals(self):
        form = GroupedChoiceDecimalTupleForm({'values': []})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_blank_grouped_choice_tuple_of_decimals(self):
        form = GroupedChoiceDecimalTupleForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'required'
        )

    def test_invalid_type_grouped_choice_tuple_of_decimals(self):
        form = GroupedChoiceDecimalTupleForm({'values': '1.1'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'invalid_list'
        )

    # Choice Max 2 String Set Form;

    def test_valid_max_2_choice_set_of_strings(self):
        form = ChoiceMax2StringSetForm({'values': ['a', 'b']})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], {'a', 'b'})

    def test_invalid_too_long_max_2_choice_set_of_strings(self):
        form = ChoiceMax2StringSetForm({'values': ['a', 'b', 'c']})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors.as_data()['values'][0].code, 'max_items'
        )

    # Choice Sorted Integer List Form:

    def test_valid_choice_sorted_list_of_integers(self):
        form = ChoiceSortedIntegerListForm({'values': [3, 1, 2]})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], [1, 2, 3])

    # Choice Optional Decimal Set Form:

    def test_valid_blank_choice_optional_set_of_decimals(self):
        form = ChoiceOptionalDecimalSetForm({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], set())

    def test_valid_empty_choice_optional_set_of_decimals(self):
        form = ChoiceOptionalDecimalSetForm({'values': []})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['values'], set())

    # HTML widgets:

    def test_html_widget_without_value(self):
        bound_field = GroupedChoiceDecimalTupleForm()['values']
        self.assertEqual(
            bound_field.as_widget(),
            '<select multiple="multiple" id="id_values" name="values"{req}>\n'
            '<optgroup label="Group 1">\n'
            '<option value="1.1">1-1</option>\n'
            '<option value="1.2">1-2</option>\n'
            '</optgroup>\n'
            '<optgroup label="Group 2">\n'
            '<option value="2.1">2-1</option>\n'
            '<option value="2.2">2-2</option>\n'
            '</optgroup>\n'
            '</select>'.format(
                req=' required' if DJANGO_110 else ''
            )
        )

    def test_html_widget_with_value(self):
        bound_field = ChoiceIntegerSetForm({'values': [1, 2]})['values']
        self.assertEqual(
            bound_field.as_widget(),
            '<select multiple="multiple" id="id_values" name="values"{req}>\n'
            '<option value="1" selected="selected">One</option>\n'
            '<option value="2" selected="selected">Two</option>\n'
            '<option value="3">Three</option>\n'
            '<option value="4">Four</option>\n</select>'.format(
                req=' required' if DJANGO_110 else ''
            )
        )


class ModelFormCollectionFieldTestCase(TestCase):

    def test_string_list_model_form_field(self):
        form_class = modelform_factory(StringListModel, fields=('values',))
        form = form_class()
        field = form.fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertEqual(field.collection_type, list)
        self.assertEqual(field.item_type, six.text_type)
        self.assertFalse(field.sort)
        self.assertIsNone(field.max_items)
        self.assertTrue(field.required)
        self.assertEqual(field.max_length, 1024)

    def test_valid_string_list_model_form_save(self):
        form_class = modelform_factory(StringListModel, fields=('values',))
        form = form_class({'values': "This,is,a,test"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], ['This', 'is', 'a', 'test']
        )
        obj = form.save()
        self.assertEqual(obj.values, ['This', 'is', 'a', 'test'])

    def test_integer_tuple_model_form_field(self):
        form_class = modelform_factory(IntegerTupleModel, fields=('values',))
        form = form_class()
        field = form.fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertEqual(field.collection_type, tuple)
        self.assertEqual(field.item_type, int)
        self.assertFalse(field.sort)
        self.assertIsNone(field.max_items)
        self.assertTrue(field.required)
        self.assertEqual(field.max_length, 1024)

    def test_valid_integer_tuple_model_form_save(self):
        form_class = modelform_factory(IntegerTupleModel, fields=('values',))
        form = form_class({'values': "12, 22, 9, -5"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], (12, 22, 9, -5)
        )
        obj = form.save()
        self.assertEqual(obj.values, (12, 22, 9, -5))

    def test_decimal_set_model_form_field(self):
        form_class = modelform_factory(DecimalSetModel, fields=('values',))
        form = form_class()
        field = form.fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertEqual(field.collection_type, set)
        self.assertEqual(field.item_type, Decimal)
        self.assertFalse(field.sort)
        self.assertIsNone(field.max_items)
        self.assertTrue(field.required)
        self.assertEqual(field.max_length, 1024)

    def test_valid_decimal_set_model_form_save(self):
        form_class = modelform_factory(DecimalSetModel, fields=('values',))
        form = form_class({'values': "3.14, 3.0, -7.77, 3.0"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'],
            {Decimal('3.14'), Decimal('3.0'), Decimal('-7.77')}
        )
        obj = form.save()
        self.assertEqual(
            obj.values, {Decimal('3.14'), Decimal('3.0'), Decimal('-7.77')}
        )

    def test_required_model_form_field_param(self):
        form_class = modelform_factory(
            OptionalIntegerTupleModel, fields=('values',)
        )
        field = form_class().fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertFalse(field.required)

    def test_unique_items_model_form_field_param(self):
        form_class = modelform_factory(
            SortedUniqueStringListModel, fields=('values',)
        )
        field = form_class().fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertTrue(field.unique_items)

    def test_sort_model_form_field_param(self):
        form_class = modelform_factory(
            SortedDecimalListModel, fields=('values',)
        )
        field = form_class().fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertTrue(field.sort)

    def test_max_items_model_form_field_param(self):
        form_class = modelform_factory(
            Max5ItemsStringListModel, fields=('values',)
        )
        field = form_class().fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertEqual(field.max_items, 5)

    def test_max_length_model_form_field_param(self):
        form_class = modelform_factory(
            Max10CharsStringListModel, fields=('values',)
        )
        field = form_class().fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertEqual(field.max_length, 10)

    def test_initial_model_form_field_param(self):
        form_class = modelform_factory(
            DefaultStringListModel, fields=('values',)
        )
        field = form_class().fields['values']
        self.assertIsInstance(field, CollectionField)
        self.assertEqual(field.initial(), ['Default', 'Values'])


class ModelFormCollectionChoiceFieldTestCase(TestCase):

    def test_choice_string_list_model_form_field(self):
        form_class = modelform_factory(
            ChoiceStringListModel, fields=('values',)
        )
        form = form_class()
        field = form.fields['values']
        self.assertIsInstance(field, CollectionChoiceField)
        self.assertEqual(field.collection_type, list)
        self.assertEqual(field.item_type, six.text_type)
        self.assertFalse(field.sort)
        self.assertIsNone(field.max_items)
        self.assertTrue(field.required)
        self.assertEqual(field.max_length, 1024)

    def test_valid_choice_string_list_model_form_save(self):
        form_class = modelform_factory(
            ChoiceStringListModel, fields=('values',)
        )
        form = form_class({'values': ['aaa', 'bbb']})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], ['aaa', 'bbb']
        )
        obj = form.save()
        self.assertEqual(obj.values, ['aaa', 'bbb'])

    def test_choice_integer_list_model_form_field(self):
        form_class = modelform_factory(
            OptionalGroupedChoiceIntegerListModel, fields=('values',)
        )
        form = form_class()
        field = form.fields['values']
        self.assertIsInstance(field, CollectionChoiceField)
        self.assertEqual(field.collection_type, list)
        self.assertEqual(field.item_type, int)
        self.assertFalse(field.sort)
        self.assertIsNone(field.max_items)
        self.assertFalse(field.required)
        self.assertEqual(field.max_length, 1024)

    def test_valid_choice_integer_list_model_form_field(self):
        form_class = modelform_factory(
            OptionalGroupedChoiceIntegerListModel, fields=('values',)
        )
        form = form_class({'values': [12, 21]})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], [12, 21]
        )
        obj = form.save()
        self.assertEqual(obj.values, [12, 21])

    def test_valid_blank_choice_integer_list_model_form_field(self):
        form_class = modelform_factory(
            OptionalGroupedChoiceIntegerListModel, fields=('values',)
        )
        form = form_class({})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data['values'], []
        )
        obj = form.save()
        self.assertEqual(obj.values, [])
